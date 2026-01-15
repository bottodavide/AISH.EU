/**
 * RichTextEditor Component
 * Descrizione: TipTap rich text editor per blog posts
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import { useEffect } from 'react';

interface RichTextEditorProps {
  content: string;
  onChange: (html: string) => void;
  placeholder?: string;
}

export function RichTextEditor({ content, onChange, placeholder }: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4],
        },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-primary underline',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full h-auto rounded-lg',
        },
      }),
    ],
    content,
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg max-w-none focus:outline-none min-h-[300px] p-4',
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  // Update editor content when prop changes (for form reset, etc.)
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);

  if (!editor) {
    return null;
  }

  const setLink = () => {
    const url = prompt('Inserisci URL:');
    if (url) {
      editor.chain().focus().setLink({ href: url }).run();
    }
  };

  const addImage = () => {
    const url = prompt('Inserisci URL immagine:');
    if (url) {
      editor.chain().focus().setImage({ src: url }).run();
    }
  };

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Toolbar */}
      <div className="bg-muted border-b p-2 flex flex-wrap gap-1">
        {/* Text Formatting */}
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('bold') ? 'bg-background font-bold' : ''
          }`}
          title="Grassetto (Ctrl+B)"
        >
          <strong>B</strong>
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('italic') ? 'bg-background' : ''
          }`}
          title="Corsivo (Ctrl+I)"
        >
          <em>I</em>
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('strike') ? 'bg-background' : ''
          }`}
          title="Barrato"
        >
          <s>S</s>
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleCode().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors font-mono ${
            editor.isActive('code') ? 'bg-background' : ''
          }`}
          title="Codice inline"
        >
          {'</>'}
        </button>

        <div className="w-px bg-border mx-1" />

        {/* Headings */}
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('heading', { level: 1 }) ? 'bg-background font-bold' : ''
          }`}
          title="Titolo H1"
        >
          H1
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('heading', { level: 2 }) ? 'bg-background font-bold' : ''
          }`}
          title="Titolo H2"
        >
          H2
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('heading', { level: 3 }) ? 'bg-background font-bold' : ''
          }`}
          title="Titolo H3"
        >
          H3
        </button>

        <div className="w-px bg-border mx-1" />

        {/* Lists */}
        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('bulletList') ? 'bg-background' : ''
          }`}
          title="Lista puntata"
        >
          • Lista
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('orderedList') ? 'bg-background' : ''
          }`}
          title="Lista numerata"
        >
          1. Lista
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors font-mono ${
            editor.isActive('codeBlock') ? 'bg-background' : ''
          }`}
          title="Blocco codice"
        >
          {'{ }'}
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('blockquote') ? 'bg-background' : ''
          }`}
          title="Citazione"
        >
          " "
        </button>

        <div className="w-px bg-border mx-1" />

        {/* Link & Image */}
        <button
          type="button"
          onClick={setLink}
          className={`px-3 py-1 rounded hover:bg-background transition-colors ${
            editor.isActive('link') ? 'bg-background' : ''
          }`}
          title="Inserisci link"
        >
          🔗
        </button>

        {editor.isActive('link') && (
          <button
            type="button"
            onClick={() => editor.chain().focus().unsetLink().run()}
            className="px-3 py-1 rounded hover:bg-background transition-colors"
            title="Rimuovi link"
          >
            🔗✕
          </button>
        )}

        <button
          type="button"
          onClick={addImage}
          className="px-3 py-1 rounded hover:bg-background transition-colors"
          title="Inserisci immagine"
        >
          🖼️
        </button>

        <div className="w-px bg-border mx-1" />

        {/* Formatting */}
        <button
          type="button"
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          className="px-3 py-1 rounded hover:bg-background transition-colors"
          title="Linea orizzontale"
        >
          ―
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().setHardBreak().run()}
          className="px-3 py-1 rounded hover:bg-background transition-colors"
          title="A capo (Shift+Enter)"
        >
          ↵
        </button>

        <div className="w-px bg-border mx-1" />

        {/* Undo/Redo */}
        <button
          type="button"
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          className="px-3 py-1 rounded hover:bg-background transition-colors disabled:opacity-50"
          title="Annulla (Ctrl+Z)"
        >
          ↶
        </button>

        <button
          type="button"
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          className="px-3 py-1 rounded hover:bg-background transition-colors disabled:opacity-50"
          title="Ripeti (Ctrl+Y)"
        >
          ↷
        </button>

        <div className="w-px bg-border mx-1" />

        {/* Clear */}
        <button
          type="button"
          onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}
          className="px-3 py-1 rounded hover:bg-background transition-colors"
          title="Rimuovi formattazione"
        >
          ✕ Clear
        </button>
      </div>

      {/* Editor */}
      <EditorContent editor={editor} />

      {/* Character count (optional) */}
      <div className="bg-muted border-t px-4 py-2 text-xs text-muted-foreground flex justify-between">
        <span>{editor.storage.characterCount?.characters() || 0} caratteri</span>
        <span>{editor.storage.characterCount?.words() || 0} parole</span>
      </div>
    </div>
  );
}
