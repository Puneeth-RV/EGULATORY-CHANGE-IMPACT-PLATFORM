import { ChangeEvent, useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, ChevronDown, Download, FileText, History, Scale, Upload } from 'lucide-react'

type Profile = { name: string; industry: string; state: string; employee_count: number | null; annual_turnover_lakh: number | null; activities: string | null; registrations: string | null }
type Report = { applicability: string; rationale: string; attributes_used: string[]; unresolved_questions: string[]; changes: Change[]; actions: Action[]; caveat: string }
type Change = { change_type: string; clause_id: string; page: number; old_page?: number; new_page?: number; confidence: number; comparison_status: string; summary: string; evidence: string; old_text?: string; new_text?: string }
type Action = { task_id?: number; action: string; reason: string; supporting_clause: string; deadline: string; priority: string; owner: string; status: string; evidence: string }
type Saved = { id: number; created_at: string; business_name: string; report: Report }
type Demo = { id: string; title: string; expected: string; profile: Profile }
type SavedProfile = { id: number; profile: Profile; updated_at: string }

const defaultProfile: Profile = { name: 'Acme Foods Pvt Ltd', industry: 'food processing', state: 'Karnataka', employee_count: 42, annual_turnover_lakh: 180, activities: 'Packaged food manufacturing and retail sale', registrations: 'FSSAI, GST' }
const fieldLabels: Record<keyof Profile, string> = { name: 'Business name', industry: 'Industry / sector', state: 'State / operating area', employee_count: 'Employees', annual_turnover_lakh: 'Annual turnover (₹ lakh)', activities: 'Key activities', registrations: 'Registrations' }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init)
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(typeof body.detail === 'string' ? body.detail : 'Request failed.') }
  return response.json()
}

function App() {
  const [profile, setProfile] = useState<Profile>(defaultProfile)
  const [earlier, setEarlier] = useState<File | null>(null)
  const [updated, setUpdated] = useState<File | null>(null)
  const [report, setReport] = useState<Report | null>(null)
  const [history, setHistory] = useState<Saved[]>([])
  const [demos, setDemos] = useState<Demo[]>([])
  const [profiles, setProfiles] = useState<SavedProfile[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [tab, setTab] = useState<'review' | 'history'>('review')
  const refreshHistory = () => request<Saved[]>('/api/reports').then(setHistory).catch(() => {})
  const refreshProfiles = () => request<SavedProfile[]>('/api/profiles').then(setProfiles).catch(() => {})
  useEffect(() => { refreshHistory(); refreshProfiles(); request<Demo[]>('/api/demos').then(setDemos).catch(() => {}) }, [])
  const setField = (key: keyof Profile, value: string) => setProfile(p => ({ ...p, [key]: ['employee_count', 'annual_turnover_lakh'].includes(key) ? (value === '' ? null : Number(value)) : value || null }))
  const saveProfile = async () => { try { await request('/api/profiles', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(profile) }); refreshProfiles(); setMessage('Business profile saved for reuse.') } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not save profile.') } }
  const run = async () => {
    if (!earlier || !updated) return
    setLoading(true); setMessage(null)
    const data = new FormData(); data.append('profile', JSON.stringify(profile)); data.append('earlier', earlier); data.append('updated', updated)
    try { const result = await request<{ id: number; report: Report }>('/api/analyses', { method: 'POST', body: data }); setReport(result.report); refreshHistory() }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Analysis failed.') }
    finally { setLoading(false) }
  }
  const runDemo = async (demo: Demo) => {
    setProfile(demo.profile); setLoading(true); setMessage(null); setTab('review')
    try { const result = await request<{ report: Report }>(`/api/demos/${demo.id}/analyses`, { method: 'POST' }); setReport(result.report); refreshHistory() }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Demo could not run.') }
    finally { setLoading(false) }
  }
  const download = () => report && window.open(URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })), '_blank')
  return <div className="shell">
    <aside className="sidebar"><div className="logo"><span><Scale size={19}/></span><b>RegImpact</b></div><p className="side-intro">Business context</p><p className="side-copy">Unknown values stay unknown; they are never interpreted as a negative answer.</p>{profiles.length > 0 && <label className="saved-profile">Reuse saved profile<select value="" onChange={e => { const item = profiles.find(p => String(p.id) === e.target.value); if (item) setProfile(item.profile) }}><option value="">Choose a saved profile</option>{profiles.map(item => <option value={item.id} key={item.id}>{item.profile.name}</option>)}</select></label>}<div className="profile-fields">{(Object.keys(fieldLabels) as (keyof Profile)[]).map(key => <label key={key}>{fieldLabels[key]}{key === 'activities' ? <textarea value={profile[key] ?? ''} onChange={e => setField(key, e.target.value)} /> : <input placeholder={['employee_count', 'annual_turnover_lakh'].includes(key) ? 'Unknown' : ''} type={['employee_count', 'annual_turnover_lakh'].includes(key) ? 'number' : 'text'} value={profile[key] ?? ''} onChange={e => setField(key, e.target.value)} />}</label>)}</div><button className="save-profile" onClick={saveProfile}>Save profile</button><div className="side-foot">Local evidence review<br/>No legal advice provided</div></aside>
    <main><header><div><p className="eyebrow">COMPLIANCE REVIEW WORKSPACE</p><h1>Regulatory change impact</h1><p className="subtitle">Understand what changed, whether it applies, and what needs to happen next.</p></div><div className="tabs"><button className={tab === 'review' ? 'active' : ''} onClick={() => setTab('review')}>Review update</button><button className={tab === 'history' ? 'active' : ''} onClick={() => setTab('history')}><History size={15}/> History</button></div></header>
    {tab === 'review' ? <><section className="steps"><div><em>01</em><b>Compare</b><span>Supply both document versions</span></div><div><em>02</em><b>Assess</b><span>Check scope against your profile</span></div><div><em>03</em><b>Act</b><span>Review source-backed next steps</span></div></section>
    <section className="panel"><div className="section-title"><div><h2>Source documents</h2><p>Upload official PDF or text copies. Identified clauses retain their page references.</p></div></div><div className="upload-grid"><UploadBox title="Earlier version" file={earlier} onChange={setEarlier}/><UploadBox title="Updated notification" file={updated} onChange={setUpdated}/></div><button className="primary" disabled={!earlier || !updated || loading} onClick={run}>{loading ? 'Creating report…' : 'Create impact report'} <span>→</span></button>{message && <div className="error"><AlertCircle size={18}/>{message}</div>}</section>
    <section className="demos"><div><h2>Judge-ready demonstrations</h2><p>Run a complete example without selecting local files.</p></div><div className="demo-list">{demos.map(d => <button className="demo" key={d.id} onClick={() => runDemo(d)} disabled={loading}><FileText size={18}/><span><b>{d.title}</b><small>Expected: {d.expected}</small></span><span>→</span></button>)}</div></section>
    {report && <Results report={report} setReport={setReport} download={download}/>}</> : <HistoryView rows={history} onOpen={row => { setReport(row.report); setTab('review') }}/>}</main></div>
}

function UploadBox({ title, file, onChange }: { title: string; file: File | null; onChange: (file: File | null) => void }) { const choose = (event: ChangeEvent<HTMLInputElement>) => onChange(event.target.files?.[0] ?? null); return <label className={'upload-box ' + (file ? 'has-file' : '')}><input type="file" accept=".pdf,.txt" onChange={choose}/>{file ? <><CheckCircle2/><b>{file.name}</b><small>{Math.max(1, Math.round(file.size / 1024))} KB · ready to compare</small></> : <><Upload/><b>{title}</b><small>Drop PDF or TXT here, or browse</small></>}</label> }
function Results({ report, setReport, download }: { report: Report; setReport: (report: Report) => void; download: () => void }) {
  const attributesUsed = report.attributes_used ?? []
  const unresolvedQuestions = report.unresolved_questions ?? []
  const updateStatus = async (index: number, status: string) => {
    const action = report.actions[index]
    if (!action.task_id) return
    try { await request(`/api/actions/${action.task_id}`, { method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({status}) }); const actions = [...report.actions]; actions[index] = {...action, status}; setReport({...report, actions}) } catch { /* Preserve display state if persistence fails. */ }
  }
  return <section className="results"><div className="result-heading"><div><p className="eyebrow">IMPACT REPORT</p><h2>Decision summary</h2></div><button className="secondary" onClick={download}><Download size={16}/> Download JSON</button></div><div className="summary"><div className={'applicability ' + report.applicability.toLowerCase().replaceAll(' ', '-')}><small>APPLICABILITY</small><b>{report.applicability}</b></div><div className="rationale"><b>Why this assessment</b><p>{report.rationale}</p>{attributesUsed.length > 0 && <p><strong>Attributes used:</strong> {attributesUsed.join(', ')}</p>}{unresolvedQuestions.length > 0 && <p><strong>Needs confirmation:</strong> {unresolvedQuestions.join(', ')}</p>}</div></div><h3>What changed</h3><div className="table">{report.changes.map((change, i) => <details key={i}><summary><span className={'pill ' + change.change_type}>{change.change_type}</span><b>{change.clause_id}</b><span>{change.summary}</span><small>Old p.{change.old_page ?? '—'} · New p.{change.new_page ?? change.page}<ChevronDown size={15}/></small></summary><div className="evidence"><b>Source evidence · {change.comparison_status === 'needs_review' ? 'review alignment' : 'matched'} · {Math.round((change.confidence ?? 1) * 100)}% confidence</b><p>{change.evidence}</p>{change.old_text && <p><strong>Earlier:</strong> {change.old_text}</p>}{change.new_text && <p><strong>Updated:</strong> {change.new_text}</p>}</div></details>)}</div><h3>What you need to do</h3><div className="actions">{report.actions.map((action, i) => <article key={i}><span className={'priority ' + action.priority.toLowerCase()}>{action.priority}</span><b>{action.action}</b>{action.reason && <p>{action.reason}</p>}<p><strong>Deadline:</strong> {action.deadline} · <strong>Owner:</strong> {action.owner}</p>{action.task_id && <label className="status">Task status<select value={action.status ?? 'Not started'} onChange={e => updateStatus(i, e.target.value)}><option>Not started</option><option>In progress</option><option>Completed</option><option>Needs review</option></select></label>}<small>{action.evidence}</small></article>)}</div><p className="caveat">{report.caveat}</p></section> }
function HistoryView({ rows, onOpen }: { rows: Saved[]; onOpen: (row: Saved) => void }) { return <section className="panel"><h2>Recent reports</h2><p className="subtitle">Saved analyses on this device.</p>{rows.length ? <div className="history">{rows.map(row => <button key={row.id} onClick={() => onOpen(row)}><FileText/><span><b>{row.business_name}</b><small>{new Date(row.created_at + 'Z').toLocaleString()}</small></span><em>{row.report.applicability}</em><span>→</span></button>)}</div> : <p className="empty">No reports saved yet. Run an analysis or a demo to create one.</p>}</section> }
export default App
