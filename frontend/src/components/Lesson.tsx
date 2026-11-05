import type { Lesson as LessonData } from "@/lib/lessons";

// Turns `backticks` in lesson text into code formatting.
function Text({ children }: { children: string }) {
  return (
    <>
      {children.split("`").map((part, i) => (i % 2 === 1 ? <code key={i}>{part}</code> : part))}
    </>
  );
}

type Props = { lesson: LessonData; onStart: () => void };

// The quick lesson at the top of each topic page, before the exercises.
export default function Lesson({ lesson, onStart }: Props) {
  return (
    <article className="lesson" aria-labelledby="lesson-title">
      <h2 id="lesson-title">Lesson</h2>
      <p className="lessonIntro"><Text>{lesson.intro}</Text></p>

      {lesson.sections.map((section) => (
        <section key={section.heading} className="lessonSection">
          <h3>{section.heading}</h3>
          <p><Text>{section.text}</Text></p>
          {section.code && <pre className="lessonCode">{section.code}</pre>}
        </section>
      ))}

      <section className="lessonSection">
        <h3>Common mistake</h3>
        <p><Text>{lesson.mistake.text}</Text></p>
        <div className="mistake">
          <div className="mistakeWrong">
            <span>✗ Wrong</span>
            <pre>{lesson.mistake.wrong}</pre>
          </div>
          <div className="mistakeRight">
            <span>✓ Right</span>
            <pre>{lesson.mistake.right}</pre>
          </div>
        </div>
      </section>

      <section className="keyPoints">
        <h3>Remember</h3>
        <ul>
          {lesson.keyPoints.map((point) => <li key={point}><Text>{point}</Text></li>)}
        </ul>
      </section>

      <button className="button" onClick={onStart}>Go to exercises</button>
    </article>
  );
}
