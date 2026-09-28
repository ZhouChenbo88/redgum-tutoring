import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

export class ValidationError extends Error {}
const fail = message => { throw new ValidationError(message); };
const word = (value, name) => {
  if (typeof value !== 'string' || !value.trim() || value.length > 250) fail(`${name} is required (maximum 250 characters).`);
  return value.trim();
};
const subjects = value => {
  if (!Array.isArray(value) || value.length === 0) fail('Enter at least one subject.');
  return [...new Set(value.map(v => word(v, 'Subject')))];
};
export const minutes = value => {
  if (typeof value !== 'string' || !/^([01]\d|2[0-3]):[0-5]\d$/.test(value)) fail('Time must use HH:MM.');
  return Number(value.slice(0, 2)) * 60 + Number(value.slice(3));
};
export const weekday = value => {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) fail('Date must use YYYY-MM-DD.');
  const date = new Date(`${value}T00:00:00Z`);
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== value) fail('Enter a valid calendar date.');
  return (date.getUTCDay() + 6) % 7;
};
export function atomicWrite(filename, data) {
  fs.mkdirSync(path.dirname(filename), { recursive: true });
  const temporary = `${filename}.${randomUUID()}.tmp`;
  let fd;
  try {
    fd = fs.openSync(temporary, 'wx', 0o600);
    fs.writeFileSync(fd, JSON.stringify(data, null, 2));
    fs.fsyncSync(fd);
    fs.closeSync(fd); fd = undefined;
    fs.renameSync(temporary, filename);
  } finally {
    if (fd !== undefined) fs.closeSync(fd);
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
  }
}

export class Scheduler {
  constructor(filename, { now = () => new Date() } = {}) {
    this.filename = filename;
    this.now = now;
    this.data = fs.existsSync(filename) ? JSON.parse(fs.readFileSync(filename, 'utf8')) : { version: 1, students: [], tutors: [], windows: [], sessions: [] };
    if (this.data.version !== 1 || ['students', 'tutors', 'windows', 'sessions'].some(key => !Array.isArray(this.data[key]))) throw new Error('Unsupported or damaged data file. Restore a verified backup.');
  }
  snapshot() { return structuredClone(this.data); }
  transaction(action) {
    const draft = this.snapshot();
    const result = action(draft);
    atomicWrite(this.filename, draft);
    this.data = draft;
    return structuredClone(result);
  }
  find(data, collection, id) {
    const item = data[collection]?.find(row => row.id === id);
    if (!item) fail(`${collection} record not found.`);
    return item;
  }
  person(data, kind, input, old) {
    const row = { ...old, ...input };
    const result = { id: old?.id ?? randomUUID(), name: word(row.name, 'Name'), subjects: subjects(row.subjects), active: row.active ?? true };
    if (typeof result.active !== 'boolean') fail('Active must be true or false.');
    if (kind === 'students') {
      result.year = Number(row.year);
      if (!Number.isInteger(result.year) || result.year < 5 || result.year > 12) fail('Year must be an integer from 5 to 12.');
      result.contact = word(row.contact, 'Family contact');
    }
    return result;
  }
  covers(data, session) {
    const day = weekday(session.date);
    const start = minutes(session.start);
    return data.windows.some(window => window.tutorId === session.tutorId && window.weekday === day && minutes(window.start) <= start && start + session.duration <= minutes(window.end));
  }
  future(session) { return new Date(`${session.date}T${session.start}:00`).getTime() > this.now().getTime(); }
  validateWindows(data, tutorId) {
    const invalid = data.sessions.filter(session => session.tutorId === tutorId && session.status === 'booked' && this.future(session) && !this.covers(data, session));
    if (invalid.length) fail(`Availability would invalidate ${invalid.length} future booked session(s). Move or cancel those sessions first.`);
  }
  session(data, input, old) {
    const row = { ...old, ...input };
    const result = { id: old?.id ?? randomUUID(), studentId: row.studentId, tutorId: row.tutorId, date: row.date, start: row.start, duration: Number(row.duration), subject: word(row.subject, 'Subject'), status: old ? row.status : 'booked' };
    weekday(result.date); minutes(result.start);
    if (![60, 90].includes(result.duration)) fail('Duration must be 60 or 90 minutes.');
    if (!['booked', 'attended', 'cancelled', 'missed'].includes(result.status)) fail('Unknown session status.');
    const student = this.find(data, 'students', result.studentId);
    const tutor = this.find(data, 'tutors', result.tutorId);
    const schedulingChanged = !old || ['studentId', 'tutorId', 'date', 'start', 'duration', 'subject'].some(key => old[key] !== result[key]) || (old.status !== 'booked' && result.status === 'booked');
    if (schedulingChanged) {
      if (!student.active || !tutor.active) fail('New or moved sessions require an active student and tutor.');
      if (!tutor.subjects.includes(result.subject)) fail('The selected tutor does not teach this subject.');
      if (!this.covers(data, result)) fail('The entire session must fit inside one tutor availability window on that weekday.');
    }
    return result;
  }
  create(kind, input) {
    if (!['students', 'tutors', 'windows', 'sessions'].includes(kind)) fail('Unknown record type.');
    return this.transaction(data => {
      let row;
      if (kind === 'students' || kind === 'tutors') row = this.person(data, kind, input);
      else if (kind === 'windows') {
        this.find(data, 'tutors', input.tutorId);
        row = { id: randomUUID(), tutorId: input.tutorId, weekday: Number(input.weekday), start: input.start, end: input.end };
        this.checkWindow(row);
      } else row = this.session(data, input);
      data[kind].push(row);
      return row;
    });
  }
  checkWindow(row) {
    if (!Number.isInteger(row.weekday) || row.weekday < 0 || row.weekday > 6) fail('Weekday must be 0 (Monday) through 6 (Sunday).');
    if (minutes(row.start) >= minutes(row.end)) fail('Availability must end after it starts.');
  }
  update(kind, id, input) {
    if (!['students', 'tutors', 'windows', 'sessions'].includes(kind)) fail('Unknown record type.');
    return this.transaction(data => {
      const old = this.find(data, kind, id);
      let row;
      if (kind === 'students' || kind === 'tutors') row = this.person(data, kind, input, old);
      else if (kind === 'windows') {
        row = { ...old, weekday: input.weekday === undefined ? old.weekday : Number(input.weekday), start: input.start ?? old.start, end: input.end ?? old.end };
        if (input.tutorId !== undefined && input.tutorId !== old.tutorId) fail('Change a window on its existing tutor; create a new window for another tutor.');
        this.checkWindow(row);
      } else row = this.session(data, input, old);
      data[kind][data[kind].findIndex(item => item.id === id)] = row;
      if (kind === 'windows') this.validateWindows(data, old.tutorId);
      return row;
    });
  }
  remove(kind, id) {
    if (kind === 'students' || kind === 'tutors') return this.update(kind, id, { active: false });
    if (kind === 'sessions') return this.update(kind, id, { status: 'cancelled' });
    if (kind !== 'windows') fail('Unknown record type.');
    return this.transaction(data => {
      const old = this.find(data, kind, id);
      data.windows = data.windows.filter(row => row.id !== id);
      this.validateWindows(data, old.tutorId);
      return old;
    });
  }
  view({ type = 'day', date, tutorId, studentId } = {}) {
    let rows = this.data.sessions;
    if (type === 'tutor') rows = rows.filter(row => row.tutorId === tutorId && row.status === 'booked' && new Date(`${row.date}T${row.start}:00`) > this.now());
    else if (type === 'student') rows = rows.filter(row => row.studentId === studentId);
    else {
      const day = weekday(date);
      let first = date, last = date;
      if (type === 'week') {
        const start = new Date(`${date}T00:00:00Z`); start.setUTCDate(start.getUTCDate() - day); first = start.toISOString().slice(0, 10);
        start.setUTCDate(start.getUTCDate() + 6); last = start.toISOString().slice(0, 10);
      } else if (type !== 'day') fail('Unknown schedule view.');
      rows = rows.filter(row => row.date >= first && row.date <= last);
    }
    return structuredClone(rows).sort((a, b) => `${a.date} ${a.start}`.localeCompare(`${b.date} ${b.start}`));
  }
}
