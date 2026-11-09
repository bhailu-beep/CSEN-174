// Home page (/): the first page visitors see.
import Link from "next/link";

export default function Home() {
  return (
    <main className="hero">
      <span className="eyebrow">Learn • Practice • Improve</span>
      <h1>
        Practice <span>C++.</span>
        <br />
        Build Your Skills.
      </h1>
      <p>Improve your C++ skills with simple coding challenges and instant feedback.</p>
      <div className="actions">
        <Link className="button" href="/signup">Get Started →</Link>
      </div>

      {/* Decorative preview of the editor. Nothing runs here. */}
      <div className="codePreview">
        <div className="fileName">solution.cpp · C++</div>
        <pre>{"int sum(int a, int b) {\n    return a + b;\n}"}</pre>
      </div>
    </main>
  );
}
