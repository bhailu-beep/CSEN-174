"use client";

import Editor, { type BeforeMount } from "@monaco-editor/react";

type Props = {
  initialValue: string; // to load different code (new exercise, Reset), give the editor a new React key
  onChange: (code: string) => void;
  readOnly?: boolean;
};

// Colors that match the site's brown/cream palette.
const addTheme: BeforeMount = (monaco) => {
  monaco.editor.defineTheme("completec", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "e8b9a0" },
      { token: "string", foreground: "c5d9a3" },
      { token: "number", foreground: "f2c879" },
      { token: "comment", foreground: "9c8580", fontStyle: "italic" },
    ],
    colors: {
      "editor.background": "#3b3030",
      "editor.lineHighlightBackground": "#4a3c3c",
      "editorLineNumber.foreground": "#8a7470",
      "editorCursor.foreground": "#fff0d1",
    },
  });
};

// Monaco is the same editor VS Code uses: C++ colors, line numbers, Tab indenting, undo, etc.
// The editor keeps track of its own text while you type (passing it back in on every keystroke drops letters).
export default function CodeEditor({ initialValue, onChange, readOnly }: Props) {
  return (
    <div className="codeEditor">
      <Editor
        height="360px"
        language="cpp"
        theme="completec"
        defaultValue={initialValue}
        onChange={(code) => onChange(code ?? "")}
        beforeMount={addTheme}
        loading={<p className="editorLoading">Loading editor…</p>}
        options={{
          fontSize: 14,
          tabSize: 4,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          automaticLayout: true,
          padding: { top: 14 },
          readOnly,
          ariaLabel: "C++ code editor",
          // Students are learning, so no pop-up autocomplete, and Enter always makes a new line.
          quickSuggestions: false,
          suggestOnTriggerCharacters: false,
          acceptSuggestionOnEnter: "off",
          wordBasedSuggestions: "off",
        }}
      />
    </div>
  );
}
