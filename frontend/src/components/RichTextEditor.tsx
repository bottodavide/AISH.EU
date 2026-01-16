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
import { useEffect, useRef, useState } from 'react';
import apiClient from '@/lib/api-client';
import { Loader2 } from 'lucide-react';

interface RichTextEditorProps {
  content: string;
  onChange: (html: string) => void;
  placeholder?: string;
}

export function RichTextEditor({ content, onChange, placeholder }: RichTextEditorProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showImageMenu, setShowImageMenu] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  // Close image menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showImageMenu) {
        setShowImageMenu(false);
      }
    };

    if (showImageMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showImageMenu]);

  if (!editor) {
    return null;
  }

  const setLink = () => {
    const url = prompt('Inserisci URL:');
    if (url) {
      editor.chain().focus().setLink({ href: url }).run();
    }
  };

  const addImageFromUrl = () => {
    const url = prompt('Inserisci URL immagine:');
    if (url) {
      editor.chain().focus().setImage({ src: url }).run();
    }
    setShowImageMenu(false);
  };

  const handleImageUploadClick = () => {
    fileInputRef.current?.click();
    setShowImageMenu(false);
  };

  const uploadAndInsertImage = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);

    try {
      // Validate file
      const validFormats = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
      if (!validFormats.includes(file.type)) {
        throw new Error('Formato non supportato. Usa JPG, PNG, WebP o GIF');
      }

      // Check size (max 300KB as per IMAGE_GUIDELINES.md for inline images)
      const sizeKB = file.size / 1024;
      if (sizeKB > 300) {
        throw new Error(`File troppo grande (${Math.round(sizeKB)} KB). Massimo: 300 KB`);
      }

      // Validate dimensions
      const dimensions = await validateImageDimensions(file);
      if (dimensions.width > 1200) {
        throw new Error(
          `Larghezza troppo grande (${dimensions.width}px). Massimo: 1200px`
        );
      }

      // Upload to backend
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', 'image');
      formData.append('is_public', 'true');
      formData.append('description', `Blog inline image - ${file.name}`);

      const response = await apiClient.post<any>('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Insert image into editor
      if (response.url) {
        editor.chain().focus().setImage({ src: response.url }).run();
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Errore durante l\'upload';
      setUploadError(errorMsg);
      alert(errorMsg);
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const validateImageDimensions = (file: File): Promise<{ width: number; height: number }> => {
    return new Promise((resolve, reject) => {
      const img = new window.Image();
      const url = URL.createObjectURL(file);

      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve({ width: img.width, height: img.height });
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Impossibile leggere le dimensioni dell\'immagine'));
      };

      img.src = url;
    });
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadAndInsertImage(file);
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

        {/* Image button with dropdown menu */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowImageMenu(!showImageMenu)}
            disabled={isUploading}
            className="px-3 py-1 rounded hover:bg-background transition-colors disabled:opacity-50 flex items-center gap-1"
            title="Inserisci immagine"
          >
            {isUploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                🖼️
                <span className="text-xs">▼</span>
              </>
            )}
          </button>

          {/* Image menu */}
          {showImageMenu && (
            <div className="absolute top-full left-0 mt-1 bg-background border rounded-lg shadow-lg z-10 min-w-[180px]">
              <button
                type="button"
                onClick={handleImageUploadClick}
                className="w-full px-4 py-2 text-left hover:bg-muted transition-colors rounded-t-lg text-sm"
              >
                📤 Carica File
              </button>
              <button
                type="button"
                onClick={addImageFromUrl}
                className="w-full px-4 py-2 text-left hover:bg-muted transition-colors rounded-b-lg text-sm"
              >
                🔗 Inserisci URL
              </button>
            </div>
          )}
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={handleFileSelect}
          className="hidden"
        />

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

      {/* Character count and upload status */}
      <div className="bg-muted border-t px-4 py-2 text-xs text-muted-foreground flex justify-between items-center">
        <div className="flex gap-4">
          <span>{editor.storage.characterCount?.characters() || 0} caratteri</span>
          <span>{editor.storage.characterCount?.words() || 0} parole</span>
        </div>
        {isUploading && (
          <div className="flex items-center gap-2 text-primary">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Caricamento immagine...</span>
          </div>
        )}
        {uploadError && (
          <span className="text-destructive">Errore upload</span>
        )}
      </div>
    </div>
  );
}
