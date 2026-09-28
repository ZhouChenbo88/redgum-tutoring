const $ = selector => document.querySelector(selector);
let data = { students: [], tutors: [], windows: [], sessions: [] };
const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const localDate = () => { const parts=new Intl.DateTimeFormat('en-CA',{timeZone:'Australia/Brisbane',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const value=type=>parts.find(part=>part.type===type).value;return `${value('year')}-${value('month')}-${value('day')}`; };
function message(text, error=false) { $('#notice').textContent = text; $('#notice').classList.toggle('error', error); }
async function api(url, method='GET', body) {
  const response = await fetch(url, { method, headers: body ? {'Content-Type':'application/json'} : {}, body: body ? JSON.stringify(body) : undefined });
  const result = await response.json(); if (!response.ok) throw new Error(result.error || 'Request failed.'); return result;
}
function button(label, action, danger=false) { const node=document.createElement('button'); node.type='button'; node.textContent=label; node.className=`small${danger?' danger':''}`; node.onclick=()=>Promise.resolve().then(action).catch(error=>message(error.message,true)); return node; }
function table(target, headings, rows) {
  const container=$(target); container.replaceChildren();
  if (!rows.length) { const empty=document.createElement('p'); empty.className='empty'; empty.textContent='No records to show. Add a record or choose another view.'; container.append(empty); return; }
  const element=document.createElement('table'), head=document.createElement('thead'), header=document.createElement('tr'), body=document.createElement('tbody');
  headings.forEach(text=>{const cell=document.createElement('th');cell.scope='col';cell.textContent=text;header.append(cell);}); head.append(header);
  rows.forEach(cells=>{const row=document.createElement('tr');cells.forEach(value=>{const cell=document.createElement('td');if(Array.isArray(value))value.forEach(node=>cell.append(node));else cell.textContent=value;row.append(cell);});body.append(row);});
  element.append(head,body);container.append(element);
}
function options(select, rows, label, activeOnly=false) {
  const previous=select.value; select.replaceChildren();
  rows.filter(row=>!activeOnly||row.active).forEach(row=>{const option=document.createElement('option');option.value=row.id;option.textContent=label(row);select.append(option);});
  if ([...select.options].some(option=>option.value===previous)) select.value=previous;
}
const name=(kind,id)=>data[kind].find(row=>row.id===id)?.name??'Unknown';
function subjects() {
  const form=$('#session-form'), tutor=data.tutors.find(row=>row.id===form.elements.tutorId.value), previous=form.elements.subject.value;
  form.elements.subject.replaceChildren();
  (tutor?.subjects??[]).forEach(value=>{const option=document.createElement('option');option.value=value;option.textContent=value;form.elements.subject.append(option);});
  if ([...form.elements.subject.options].some(option=>option.value===previous))form.elements.subject.value=previous;
  const windows=data.windows.filter(row=>row.tutorId===tutor?.id).map(row=>`${days[row.weekday]} ${row.start}–${row.end}`);
  $('#window-hint').textContent=windows.length?`Available: ${windows.join('; ')}. Whole session must fit in one window.`:'This tutor has no availability windows yet.';
}
function edit(formId,row,title) {
  const form=$(`#${formId}`); reset(formId);
  const map={ 'student-form':'students', 'tutor-form':'tutors', 'session-form':'schedule', 'window-form':'tutors' }; showPane(map[formId]);
  if(formId==='session-form') {
    // Historic records can still be inspected when a linked person is inactive.
    options(form.elements.studentId,data.students,row=>`${row.name}${row.active?'':' (inactive)'}`);
    options(form.elements.tutorId,data.tutors,row=>`${row.name}${row.active?'':' (inactive)'}`);
  }
  Object.entries(row).forEach(([key,value])=>{ if(form.elements[key]) form.elements[key].value=Array.isArray(value)?value.join(', '):String(value); });
  if(formId==='session-form'){subjects();form.elements.subject.value=row.subject;form.elements.status.disabled=false;}
  $(`#${formId.replace('-form','-title')}`).textContent=title;
  form.scrollIntoView({behavior:'smooth',block:'start'});
}
function reset(formId) {
  const form=$(`#${formId}`);form.reset();form.elements.id.value='';
  const titles={'student-form':'Add a student','tutor-form':'Add a tutor','window-form':'Add availability','session-form':'Book a session'};
  $(`#${formId.replace('-form','-title')}`).textContent=titles[formId];
  if(formId==='session-form'){ options(form.elements.studentId,data.students,row=>row.name,true);options(form.elements.tutorId,data.tutors,row=>row.name,true);form.elements.date.value=localDate();form.elements.status.disabled=true;subjects(); }
}
async function remove(kind,id) {if(!confirm(kind==='windows'?'Remove this availability window?':'Preserve this record and mark it inactive/cancelled?'))return;await api(`/api/${kind}/${id}`,'DELETE');await load();message('Record updated and saved.');}
function people() {
  const studentQuery=$('#student-search').value.toLowerCase(),tutorQuery=$('#tutor-search').value.toLowerCase();
  table('#student-list',['Student','Year / subjects','Contact','State','Actions'],data.students.filter(row=>`${row.name} ${row.contact} ${row.subjects}`.toLowerCase().includes(studentQuery)).map(row=>[row.name,`${row.year} · ${row.subjects.join(', ')}`,row.contact,row.active?'Active':'Inactive',[button('Edit',()=>edit('student-form',row,'Edit student')),button('History',async()=>{showPane('schedule');$('#view').value='student';$('#view-student').value=row.id;await schedule();}),...(row.active?[button('Deactivate',()=>remove('students',row.id),true)]:[])]]));
  table('#tutor-list',['Tutor','Subjects','State','Actions'],data.tutors.filter(row=>`${row.name} ${row.subjects}`.toLowerCase().includes(tutorQuery)).map(row=>[row.name,row.subjects.join(', '),row.active?'Active':'Inactive',[button('Edit',()=>edit('tutor-form',row,'Edit tutor')),button('Upcoming',async()=>{showPane('schedule');$('#view').value='tutor';$('#view-tutor').value=row.id;await schedule();}),...(row.active?[button('Deactivate',()=>remove('tutors',row.id),true)]:[])]]));
  table('#window-list',['Tutor','Day','Window','Actions'],data.windows.map(row=>[name('tutors',row.tutorId),days[row.weekday],`${row.start}–${row.end}`,[button('Edit',()=>edit('window-form',row,'Edit availability')),button('Remove',()=>remove('windows',row.id),true)]]));
}
async function schedule() {
  const type=$('#view').value;
  $('#date-label').hidden=!['day','week'].includes(type);$('#student-label').hidden=type!=='student';$('#tutor-label').hidden=type!=='tutor';
  const query=new URLSearchParams({type,date:$('#view-date').value,tutorId:$('#view-tutor').value,studentId:$('#view-student').value});
  const rows=await api(`/api/schedule?${query}`);$('#count').textContent=`${rows.length} session${rows.length===1?'':'s'}`;
  table('#session-list',['When','Student','Tutor / subject','Length','Status','Actions'],rows.map(row=>[`${row.date} ${row.start}`,name('students',row.studentId),`${name('tutors',row.tutorId)} · ${row.subject}`,`${row.duration} min`,row.status,[button('Edit / move',()=>edit('session-form',row,'Edit or move session')), ...(row.status!=='cancelled'?[button('Cancel',()=>remove('sessions',row.id),true)]:[])]]));
}
async function load() {
  data=await api('/api/state');
  options($('#view-student'),data.students,row=>row.name);options($('#view-tutor'),data.tutors,row=>row.name);
  const form=$('#session-form');
  if(!form.elements.id.value){options(form.elements.studentId,data.students,row=>row.name,true);options(form.elements.tutorId,data.tutors,row=>row.name,true);subjects();}
  options($('#window-form').elements.tutorId,data.tutors,row=>row.name);
  people();await schedule();
}
function showPane(id) {document.querySelectorAll('.pane').forEach(pane=>pane.hidden=pane.id!==id);document.querySelectorAll('nav button').forEach(button=>button.classList.toggle('selected',button.dataset.pane===id));}
document.querySelectorAll('[data-pane]').forEach(button=>button.onclick=()=>showPane(button.dataset.pane));
document.querySelectorAll('[data-reset]').forEach(button=>button.onclick=()=>reset(button.dataset.reset));
for(const [formId,kind] of [['student-form','students'],['tutor-form','tutors'],['window-form','windows'],['session-form','sessions']]){
  $(`#${formId}`).onsubmit=async event=>{
    event.preventDefault();const form=event.currentTarget,submit=form.querySelector('[type="submit"],button:not([type])');
    try {if(submit)submit.disabled=true;const payload=Object.fromEntries(new FormData(form)),id=payload.id;delete payload.id;
      if(payload.subjects)payload.subjects=payload.subjects.split(',').map(value=>value.trim()).filter(Boolean);
      if(payload.active!==undefined)payload.active=payload.active==='true';
      await api(`/api/${kind}${id?`/${id}`:''}`,id?'PATCH':'POST',payload);reset(formId);await load();message('Saved. Your records persist when the server restarts.');
    }catch(error){message(error.message,true);}finally{if(submit)submit.disabled=false;}
  };
}
$('#session-form').elements.tutorId.onchange=subjects;
$('#student-search').oninput=people;$('#tutor-search').oninput=people;
$('#refresh').onclick=()=>schedule().catch(error=>message(error.message,true));$('#view').onchange=()=>schedule().catch(error=>message(error.message,true));
$('#view-date').value=localDate();$('#session-form').elements.date.value=localDate();
load().then(()=>message('Ready. Add fictional students and tutors, then set tutor availability.')).catch(error=>message(error.message,true));
