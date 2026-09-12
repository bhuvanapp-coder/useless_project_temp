import { useRef, useState } from 'react'
import { generateUselessLesson, generateUselessQuestions, refuseActualTopic, uploadPdf } from './services/api'

const navItems = [
  { id: 'landing', label: 'Home' },
  { id: 'upload', label: 'Upload' },
  { id: 'lesson', label: 'Lesson' },
  { id: 'exam', label: 'Exam questions' },
]

const uselessFacts = [
  ['Pages inspected', '42'],
  ['Tables found', '7-ish'],
  ['Important ideas', '0'],
]

function App() {
  const [activePage, setActivePage] = useState('landing')
  const [file, setFile] = useState(null)
  const [document, setDocument] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')
  const [lesson, setLesson] = useState(null)
  const [isGeneratingLesson, setIsGeneratingLesson] = useState(false)
  const [lessonError, setLessonError] = useState('')
  const [exam, setExam] = useState(null)
  const [isGeneratingExam, setIsGeneratingExam] = useState(false)
  const [examError, setExamError] = useState('')
  const [quizStarted, setQuizStarted] = useState(false)
  const [quizAnswers, setQuizAnswers] = useState({})
  const [quizGrade, setQuizGrade] = useState(null)
  const [refusal, setRefusal] = useState(null)
  const [isRefusing, setIsRefusing] = useState(false)
  const [refusalError, setRefusalError] = useState('')

  function choosePage(page) {
    setActivePage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function handleFile(selectedFile) {
    if (!selectedFile) return
    if (selectedFile.type !== 'application/pdf' && !selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('That is not a PDF. The academic assistant is disappointed but not surprised.')
      return
    }
    setFile(selectedFile)
    setError('')
  }

  async function uploadSelectedFile() {
    if (!file) {
      setError('Choose a PDF before uploading it. The assistant cannot study the upload button.')
      return
    }
    setDocument(null)
    setLesson(null)
    setLessonError('')
    setExam(null)
    setExamError('')
    setQuizStarted(false)
    setQuizAnswers({})
    setQuizGrade(null)
    setRefusal(null)
    setRefusalError('')
    setError('')
    setIsProcessing(true)

    try {
      const uploadResult = await uploadPdf(file)
      setDocument(uploadResult.document)
      choosePage('lesson')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsProcessing(false)
    }
  }

  async function generateLesson() {
    if (!document) {
      setLessonError('Upload a PDF first. The assistant cannot prioritize the margins of nothing.')
      return
    }
    setLessonError('')
    setIsGeneratingLesson(true)
    try {
      const generatedLesson = await generateUselessLesson(document, 'Teach me the most important thing in this PDF.')
      setLesson(generatedLesson)
    } catch (requestError) {
      setLessonError(requestError.message)
    } finally {
      setIsGeneratingLesson(false)
    }
  }

  async function generateExam() {
    if (!document) {
      setExamError('Upload a PDF first. An exam about nothing would be irresponsibly easy.')
      return
    }
    setExamError('')
    setIsGeneratingExam(true)
    try {
      const generatedExam = await generateUselessQuestions(document)
      setExam(generatedExam)
    } catch (requestError) {
      setExamError(requestError.message)
    } finally {
      setIsGeneratingExam(false)
    }
  }

  function startQuiz() {
    setQuizStarted(true)
    setQuizAnswers({})
    setQuizGrade(null)
  }

  function submitQuiz(questions) {
    const correct = questions.filter((question) => quizAnswers[question.id] === question.answer).length
    setQuizGrade({ correct, total: questions.length })
  }


  async function refuseActualTopicRequest() {
    if (!document) {
      setRefusalError('There is no document, and therefore no useful information to ignore.')
      return
    }
    setRefusalError('')
    setIsRefusing(true)
    try {
      const result = await refuseActualTopic(document, 'the actual academic topic')
      setRefusal(result.text || result)
    } catch (requestError) {
      setRefusalError(requestError.message)
    } finally {
      setIsRefusing(false)
    }
  }

  return (
    <div className="min-h-screen overflow-hidden bg-[#f5f1e8] text-[#29251f]">
      <div className="pointer-events-none fixed -right-24 -top-32 h-96 w-96 rounded-full bg-[#f1c7b5]/50 blur-3xl" />
      <Navigation activePage={activePage} choosePage={choosePage} />
      <main className="relative mx-auto max-w-7xl px-5 pb-16 sm:px-8 lg:px-12">
        {activePage === 'landing' && <Landing choosePage={choosePage} />}
        {activePage === 'upload' && <Upload file={file} handleFile={handleFile} uploadSelectedFile={uploadSelectedFile} isProcessing={isProcessing} error={error} />}
        {activePage === 'lesson' && <Lesson document={document} lesson={lesson} isGenerating={isGeneratingLesson} error={lessonError} generateLesson={generateLesson} refusal={refusal} isRefusing={isRefusing} refusalError={refusalError} refuseActualTopic={refuseActualTopicRequest} choosePage={choosePage} />}
        {activePage === 'exam' && <ExamQuestions document={document} exam={exam} isGenerating={isGeneratingExam} error={examError} generateExam={generateExam} quizStarted={quizStarted} quizAnswers={quizAnswers} quizGrade={quizGrade} setQuizAnswers={setQuizAnswers} startQuiz={startQuiz} submitQuiz={submitQuiz} choosePage={choosePage} />}
      </main>
      <footer className="mx-auto flex max-w-7xl flex-col gap-2 border-t border-[#d9d0c4] px-5 py-6 font-mono text-[10px] uppercase tracking-[0.16em] text-[#8c8276] sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-12">
        <span>For educational purposes. Unfortunately.</span>
        <span>NBNTN / 2026</span>
      </footer>
    </div>
  )
}

function Navigation({ activePage, choosePage }) {
  return (
    <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between border-b border-[#d9d0c4] px-5 py-5 sm:px-8 lg:px-12">
      <button onClick={() => choosePage('landing')} className="group flex items-center gap-3 text-left">
        <span className="grid h-9 w-9 place-items-center bg-[#d85c40] font-display text-xl text-[#fffaf1] shadow-[4px_4px_0_#29251f] transition-transform group-hover:-translate-y-0.5">N</span>
        <span className="hidden font-mono text-[11px] font-bold uppercase tracking-[0.12em] sm:block">Notes but not<br />the notes</span>
      </button>
      <nav className="hidden items-center gap-1 lg:flex">
        {navItems.slice(1).map((item) => <NavButton key={item.id} item={item} activePage={activePage} choosePage={choosePage} />)}
      </nav>
      <button onClick={() => choosePage('upload')} className="rounded-full border border-[#29251f] bg-[#29251f] px-4 py-2 font-mono text-[10px] uppercase tracking-[0.12em] text-[#fffaf1] transition hover:bg-[#d85c40] hover:text-[#29251f]">Start studying →</button>
    </header>
  )
}

function NavButton({ item, activePage, choosePage }) {
  return <button onClick={() => choosePage(item.id)} className={`rounded-full px-3 py-2 font-mono text-[10px] uppercase tracking-[0.1em] transition ${activePage === item.id ? 'bg-[#e7ddd0] text-[#d85c40]' : 'text-[#756c61] hover:bg-[#ebe4d8]'}`}>{item.label}</button>
}

function Landing({ choosePage }) {
  return <>
    <section className="grid items-end gap-10 pb-18 pt-20 lg:grid-cols-[1.15fr_0.85fr] lg:pt-28">
      <div className="animate-[fadeUp_700ms_ease-out]">
        <p className="mb-6 font-mono text-[11px] font-bold uppercase tracking-[0.2em] text-[#d85c40]">The anti-study companion / 001</p>
        <h1 className="max-w-4xl font-display text-6xl leading-[0.88] tracking-[-0.055em] sm:text-8xl lg:text-[8.4rem]">Notes but<br /><span className="text-[#d85c40] italic">not</span> the notes.</h1>
        <p className="mt-8 max-w-lg text-xl leading-relaxed text-[#756c61] sm:text-2xl">Give us your notes. We’ll make sure you learn absolutely nothing useful.</p>
        <div className="mt-10 flex flex-wrap items-center gap-4">
          <button onClick={() => choosePage('upload')} className="bg-[#d85c40] px-6 py-4 font-mono text-xs font-bold uppercase tracking-[0.12em] text-[#fffaf1] shadow-[5px_5px_0_#29251f] transition hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[3px_3px_0_#29251f]">Upload your notes <span className="ml-8 text-lg">↗</span></button>
          <span className="font-mono text-[10px] uppercase tracking-[0.1em] text-[#968b7e]">No useful knowledge guaranteed</span>
        </div>
      </div>
      <SampleOutput />
    </section>
    <section className="grid border-y border-[#d9d0c4] py-7 sm:grid-cols-3">
      {uselessFacts.map(([label, value], index) => <div key={label} className={`px-4 ${index > 0 ? 'border-l border-[#d9d0c4]' : ''}`}><p className="font-mono text-[10px] uppercase tracking-[0.12em] text-[#968b7e]">{label}</p><p className="mt-1 font-display text-3xl text-[#d85c40]">{value}</p></div>)}
    </section>
    <section className="grid gap-10 py-20 lg:grid-cols-3">
      <div><p className="font-mono text-[10px] uppercase tracking-[0.15em] text-[#d85c40]">The workflow</p><h2 className="mt-4 font-display text-4xl leading-none">A three-step<br /><i>academic detour.</i></h2></div>
      <Step number="01" title="Upload" text="Feed the machine a PDF full of things you were supposed to remember." />
      <Step number="02" title="Get distracted" text="Receive a lesson about page margins, author names, and suspiciously blank pages." />
    </section>
  </>
}

function Step({ number, title, text }) {
  return <div className="border-t border-[#29251f] pt-4"><span className="font-mono text-xs text-[#d85c40]">{number}</span><h3 className="mt-8 font-display text-3xl">{title}</h3><p className="mt-3 leading-relaxed text-[#756c61]">{text}</p></div>
}

function SampleOutput() {
  return <div className="relative rotate-2 border border-[#29251f] bg-[#fbf8f1] p-6 shadow-[10px_10px_0_#decfc0] sm:p-8"><div className="flex items-center justify-between border-b border-[#d9d0c4] pb-4 font-mono text-[10px] uppercase tracking-[0.15em] text-[#968b7e]"><span>Sample lesson</span><span>01 / 04</span></div><p className="mt-8 font-mono text-xs uppercase tracking-[0.12em] text-[#d85c40]">The AI has spoken</p><h2 className="mt-4 font-display text-4xl leading-none">Unit 3 starts on page 17.</h2><p className="mt-5 text-lg leading-relaxed text-[#756c61]">Page 17 is an excellent page because it comes after page 16. It also has a margin that is approximately 1.2 inches wide. Remarkable.</p><div className="mt-8 flex gap-2">{['page 17', '1.2 in margin', 'very factual'].map((tag) => <span key={tag} className="border border-[#d9d0c4] px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-[#968b7e]">{tag}</span>)}</div></div>
}

function Upload({ file, handleFile, uploadSelectedFile, isProcessing, error }) {
  const inputRef = useRef(null)
  return <PageIntro eyebrow="Upload / 02" title="Give us something to misunderstand." description="Choose a course PDF and we’ll inspect every detail except the ones you actually need.">
    <div className="mx-auto max-w-3xl">
      <input ref={inputRef} type="file" accept="application/pdf" hidden onChange={(event) => handleFile(event.target.files?.[0])} />
      <button onClick={() => inputRef.current?.click()} className={`group flex min-h-80 w-full flex-col items-center justify-center border-2 border-dashed p-8 text-center transition ${file ? 'border-[#d85c40] bg-[#f6dfd5]' : 'border-[#b9aea1] bg-[#fbf8f1] hover:border-[#d85c40] hover:bg-[#f6dfd5]'}`}><span className="grid h-16 w-14 place-items-center border border-[#d85c40] font-mono text-xs text-[#d85c40] transition group-hover:-rotate-6">PDF</span><strong className="mt-6 font-display text-3xl">{file ? file.name : 'Drop your notes here'}</strong><span className="mt-2 font-mono text-[10px] uppercase tracking-[0.14em] text-[#968b7e]">{file ? 'Ready to make this less useful' : 'or click to browse / PDF only'}</span></button>
      {error && <p className="mt-4 font-mono text-xs text-[#b34e38]">{error}</p>}
      <div className="mt-5 flex flex-wrap items-start justify-between gap-5 font-mono text-[10px] uppercase tracking-[0.1em] text-[#968b7e]"><span>Warning: side effects may include knowing the exact number of blank pages.</span><button type="button" onClick={uploadSelectedFile} disabled={!file || isProcessing} className="shrink-0 bg-[#29251f] px-5 py-3 font-mono text-xs font-bold uppercase tracking-wider text-[#fffaf1] transition hover:bg-[#d85c40] disabled:cursor-not-allowed disabled:opacity-40">{isProcessing ? 'Uploading...' : 'Upload PDF →'}</button></div>
    </div>
  </PageIntro>
}

function Lesson({ document, lesson, isGenerating, error, generateLesson, refusal, isRefusing, refusalError, refuseActualTopic, choosePage }) {
  return <PageIntro eyebrow="Lesson / 04" title="Your lesson is ready." description="We have translated the document into the only knowledge that truly lasts: trivia about the document itself.">
    {!lesson && !isGenerating && !error && <div className="border border-dashed border-[#b9aea1] bg-[#fbf8f1] p-8 text-center sm:p-12"><p className="font-display text-3xl">The PDF is waiting to be spectacularly misunderstood.</p><button onClick={generateLesson} className="mt-8 bg-[#d85c40] px-7 py-5 font-mono text-sm font-bold uppercase tracking-[0.14em] text-[#fffaf1] shadow-[5px_5px_0_#29251f] transition hover:translate-x-0.5 hover:translate-y-0.5">Teach me something <span className="ml-8">↗</span></button></div>}
    {isGenerating && <LessonLoading />}
    {error && <div className="border border-[#d85c40] bg-[#f6dfd5] p-6 font-mono text-sm text-[#b34e38]"><strong>Lesson interrupted:</strong> {error}<button onClick={generateLesson} className="mt-5 block border-b border-[#b34e38] pb-1 text-xs uppercase tracking-wider">Try again →</button></div>}
    {lesson && !isGenerating && <LessonResult lesson={lesson} document={document} refusal={refusal} isRefusing={isRefusing} refusalError={refusalError} refuseActualTopic={refuseActualTopic} choosePage={choosePage} />}
  </PageIntro>
}

function LessonLoading() {
  return <div className="border border-[#d9d0c4] bg-[#fbf8f1] p-8 text-center sm:p-12"><div className="mx-auto flex h-20 items-center justify-center gap-2"><span className="h-4 w-4 animate-bounce rounded-full bg-[#d85c40] [animation-delay:-0.3s]" /><span className="h-4 w-4 animate-bounce rounded-full bg-[#d85c40] [animation-delay:-0.15s]" /><span className="h-4 w-4 animate-bounce rounded-full bg-[#d85c40]" /></div><p className="font-display text-3xl">Consulting the footer...</p><p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-[#968b7e]">The important nonsense is being assembled</p></div>
}

function LessonResult({ lesson, document, refusal, isRefusing, refusalError, refuseActualTopic, choosePage }) {
  return <><div className="border border-[#29251f] bg-[#fbf8f1] p-6 shadow-[8px_8px_0_#decfc0] sm:p-10"><div className="flex flex-wrap justify-between gap-3 border-b border-[#d9d0c4] pb-5 font-mono text-[10px] uppercase tracking-wider text-[#968b7e]"><span>Generated lesson / document trivia</span><span>{document?.title || 'Uploaded PDF'}</span></div><h2 className="mt-8 max-w-3xl font-display text-4xl leading-none sm:text-6xl">{lesson.title}</h2><p className="mt-7 max-w-2xl text-xl leading-relaxed text-[#756c61]">{lesson.explanation}</p><div className="mt-10 grid gap-4 border-t border-[#d9d0c4] pt-6 sm:grid-cols-2">{[['Key points', lesson.key_points], ['Fake importance', lesson.fake_importance], ['Memory trick', lesson.memory_trick], ['Exam relevance', lesson.exam_relevance]].map(([label, value]) => <div key={label} className="border border-[#d9d0c4] bg-[#f5f1e8] p-4"><p className="font-mono text-[10px] uppercase tracking-wider text-[#d85c40]">{label}</p>{Array.isArray(value) ? <ul className="mt-3 list-inside list-disc space-y-1 text-sm leading-relaxed text-[#756c61]">{value.map((point) => <li key={point}>{point}</li>)}</ul> : <p className="mt-3 text-lg leading-relaxed text-[#756c61]">{value}</p>}</div>)}</div></div><div className="mt-10 border-2 border-dashed border-[#29251f] bg-[#29251f] p-6 text-[#fffaf1] sm:p-8"><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#f1c7b5]">Final academic service</p><h3 className="mt-3 font-display text-3xl sm:text-4xl">Ready to learn the actual topic?</h3><p className="mt-3 max-w-xl text-[#e7ddd0]">We can fix that immediately by refusing to do it.</p><button onClick={refuseActualTopic} disabled={isRefusing} className="mt-6 bg-[#d85c40] px-5 py-4 font-mono text-xs font-bold uppercase tracking-[0.12em] text-[#fffaf1] transition hover:bg-[#f1c7b5] hover:text-[#29251f] disabled:cursor-wait disabled:opacity-60">{isRefusing ? 'Locating useful information...' : 'Teach Me The Actual Topic'} <span className="ml-5">↗</span></button>{refusalError && <p className="mt-4 font-mono text-xs text-[#f1c7b5]">{refusalError}</p>}{isRefusing && <p className="mt-4 animate-pulse font-mono text-xs text-[#f1c7b5]">Warning: meaningful content detected.</p>}{refusal && <div className="mt-6 rotate-[-1deg] border border-[#f1c7b5]/50 bg-[#fffaf1] p-5 text-[#29251f] shadow-[5px_5px_0_#d85c40]"><p className="font-mono text-[10px] uppercase tracking-[0.15em] text-[#d85c40]">Useful information not found</p><p className="mt-3 font-display text-2xl leading-tight">{refusal}</p><p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-[#968b7e]">The application remains committed to its values.</p></div>}</div><button onClick={() => choosePage('exam')} className="mt-8 border-b border-[#d85c40] pb-1 font-mono text-xs uppercase tracking-wider text-[#d85c40]">Test my useless knowledge →</button></>
}

function ExamQuestions({ document, exam, isGenerating, error, generateExam, quizStarted, quizAnswers, quizGrade, setQuizAnswers, startQuiz, submitQuiz, choosePage }) {
  const quizQuestions = buildQuizQuestions(document)
  return <PageIntro eyebrow="Exam questions / 05" title="🔥 Most important exam questions" description={document ? `A formal assessment of the least useful facts found in ${document.title || 'your PDF'}.` : 'Upload a PDF to generate serious-looking questions about completely unserious details.'}>
    {!exam && !isGenerating && !error && <div className="border border-[#29251f] bg-[#fbf8f1] p-8 shadow-[8px_8px_0_#decfc0] sm:p-12"><div className="flex items-center justify-between border-b border-[#d9d0c4] pb-5 font-mono text-[10px] uppercase tracking-[0.15em] text-[#756c61]"><span>Examination board / NBNTN</span><span>Paper 01</span></div><div className="py-10"><p className="font-display text-4xl leading-none sm:text-6xl">Prove you were paying attention to the wrong things.</p><p className="mt-6 max-w-2xl text-lg leading-relaxed text-[#756c61]">Questions will be based on pages, names, repeated phrases, and other material of absolutely no academic consequence.</p></div><button onClick={generateExam} className="bg-[#29251f] px-6 py-4 font-mono text-xs font-bold uppercase tracking-[0.14em] text-[#fffaf1] transition hover:bg-[#d85c40]">Generate exam paper <span className="ml-8">→</span></button></div>}
    {isGenerating && <ExamLoading />}
    {error && <div className="border border-[#d85c40] bg-[#f6dfd5] p-6 font-mono text-sm text-[#b34e38]"><strong>Examination cancelled:</strong> {error}<button onClick={generateExam} className="mt-5 block border-b border-[#b34e38] pb-1 text-xs uppercase tracking-wider">Regenerate paper →</button></div>}
    {exam && !isGenerating && !quizStarted && <ExamPaper exam={exam} startQuiz={startQuiz} />}
    {quizStarted && <Quiz questions={quizQuestions} answers={quizAnswers} grade={quizGrade} setAnswers={setQuizAnswers} submitQuiz={submitQuiz} choosePage={choosePage} />}
  </PageIntro>
}

function ExamLoading() {
  return <div className="border border-[#d9d0c4] bg-[#fbf8f1] p-10 text-center"><div className="mx-auto mb-7 h-14 w-14 animate-spin rounded-full border-4 border-[#e7ddd0] border-t-[#d85c40]" /><p className="font-display text-3xl">Marking the margins...</p><p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-[#968b7e]">Compiling questions no professor requested</p></div>
}

function ExamPaper({ exam, startQuiz }) {
  return <><div className="border border-[#29251f] bg-[#fbf8f1] shadow-[8px_8px_0_#decfc0]"><div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-[#29251f] p-6 font-mono text-[10px] uppercase tracking-[0.14em] sm:p-8"><span>NBNTN Department of Irrelevant Assessment</span><span>Time: far too much</span></div><div className="border-b border-[#d9d0c4] px-6 py-5 sm:px-8"><h2 className="font-display text-3xl">{exam.title}</h2><p className="mt-2 font-mono text-[10px] uppercase tracking-wider text-[#968b7e]">Candidate: ____________________ &nbsp; Score: ______ / completely arbitrary</p></div><div className="divide-y divide-[#d9d0c4]">{exam.questions.map((item, index) => <article key={item.question} className="p-6 sm:p-8"><div className="flex items-start gap-4"><span className="font-mono text-sm font-bold text-[#d85c40]">0{index + 1}</span><div className="min-w-0 flex-1"><h3 className="font-display text-2xl leading-tight">{item.question}</h3><div className="mt-4 flex flex-wrap gap-2 font-mono text-[9px] uppercase tracking-wider text-[#756c61]"><span className="border border-[#d9d0c4] px-2 py-1">{item.fake_marks}</span><span className="border border-[#d9d0c4] px-2 py-1">Difficulty: {item.fake_difficulty}</span></div><p className="mt-4 border-l-2 border-[#d85c40] pl-3 text-sm italic leading-relaxed text-[#756c61]">Examiner's note: {item.ridiculous_explanation}</p></div></div></article>)}</div></div><button onClick={startQuiz} className="mt-8 bg-[#d85c40] px-6 py-4 font-mono text-xs font-bold uppercase tracking-[0.14em] text-[#fffaf1]">Begin multiple-choice quiz →</button></>
}

function buildQuizQuestions(document) {
  const page = document?.pages?.[0]?.detected_page_number || document?.pages?.[0]?.page_number || 1
  const pageCount = document?.page_count || 1
  const author = document?.author || 'The mysterious author'
  const title = document?.title || 'The uploaded document'
  return [
    { id: 'page', question: 'Which page deserves an entirely unreasonable amount of attention?', options: [`Page ${page}`, 'The cover only', 'The printer settings', 'Page 404'], answer: `Page ${page}` },
    { id: 'count', question: 'How many pages are in the document?', options: [String(pageCount), '7-ish', 'An emotionally significant number', 'Zero useful pages'], answer: String(pageCount) },
    { id: 'author', question: 'Who is credited as the author?', options: [author, 'The footer', 'The examination board', 'A very confident margin'], answer: author },
    { id: 'title', question: 'What is the document called?', options: [title, 'Untitled (Very Important)', 'Page 17', 'The Big Footer'], answer: title },
  ]
}

function Quiz({ questions, answers, grade, setAnswers, submitQuiz }) {
  return <div className="border-2 border-[#29251f] bg-[#fbf8f1] shadow-[8px_8px_0_#decfc0]"><div className="border-b-2 border-[#29251f] p-6 sm:p-8"><p className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#d85c40]">Quiz paper / multiple choice</p><h2 className="mt-3 font-display text-4xl">Select the correct useless answer.</h2><p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-[#968b7e]">Every question is worth one completely fake point.</p></div><div className="divide-y divide-[#d9d0c4]">{questions.map((question, index) => <article key={question.id} className="p-6 sm:p-8"><h3 className="font-display text-2xl"><span className="mr-3 font-mono text-sm text-[#d85c40]">0{index + 1}</span>{question.question}</h3><div className="mt-5 grid gap-2 sm:grid-cols-2">{question.options.map((option) => <label key={option} className={`flex cursor-pointer items-center gap-3 border p-4 font-mono text-xs transition ${answers[question.id] === option ? 'border-[#d85c40] bg-[#f6dfd5] text-[#b34e38]' : 'border-[#d9d0c4] bg-[#f5f1e8] hover:border-[#d85c40]'}`}><input type="radio" name={question.id} checked={answers[question.id] === option} onChange={() => setAnswers((current) => ({ ...current, [question.id]: option }))} className="accent-[#d85c40]" />{option}</label>)}</div></article>)}</div><div className="flex flex-wrap items-center justify-between gap-4 border-t-2 border-[#29251f] p-6 sm:p-8"><button onClick={() => submitQuiz(questions)} className="bg-[#29251f] px-6 py-4 font-mono text-xs font-bold uppercase tracking-[0.14em] text-[#fffaf1] transition hover:bg-[#d85c40]">Submit quiz →</button>{grade && <div className="border border-[#d85c40] bg-[#f6dfd5] px-5 py-3"><p className="font-mono text-[10px] uppercase tracking-wider text-[#b34e38]">Final grade</p><p className="font-display text-3xl text-[#d85c40]">{grade.correct} / {grade.total}</p><p className="font-mono text-[10px] uppercase text-[#756c61]">{grade.correct === grade.total ? 'Perfectly useless.' : 'A promising lack of relevance.'}</p></div>}</div></div>
}

function PageIntro({ eyebrow, title, description, children }) {
  return <section className="animate-[fadeUp_500ms_ease-out] py-16 sm:py-24"><div className="mb-14 max-w-3xl"><p className="font-mono text-[10px] font-bold uppercase tracking-[0.18em] text-[#d85c40]">{eyebrow}</p><h1 className="mt-5 font-display text-6xl leading-[0.9] tracking-[-0.05em] sm:text-8xl">{title}</h1><p className="mt-6 max-w-xl text-lg leading-relaxed text-[#756c61]">{description}</p></div>{children}</section>
}

export default App
