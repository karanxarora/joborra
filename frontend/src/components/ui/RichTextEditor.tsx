import React, { useRef, useEffect, useState } from 'react';
import { Bold, Italic, List, Type } from 'lucide-react';

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  value,
  onChange,
  placeholder = "Enter text...",
  className = ""
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (editorRef.current && editorRef.current.innerHTML !== value) {
      editorRef.current.innerHTML = value || '';
    }
  }, [value]);

  const handleInput = () => {
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
    handleInput();
  };

  const insertBulletList = () => {
    if (editorRef.current) {
      editorRef.current.focus();
      
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        let container: Node | null = range.commonAncestorContainer;
        
        // Walk up the DOM tree to find if we're in a list
        while (container && container !== editorRef.current) {
          if (container.nodeType === Node.ELEMENT_NODE) {
            const element = container as Element;
            if (element.tagName === 'UL') {
              // Already in a bullet list, just add a new item
              const newLi = document.createElement('li');
              newLi.innerHTML = '<br>';
              range.insertNode(newLi);
              range.setStart(newLi, 0);
              range.setEnd(newLi, 0);
              selection.removeAllRanges();
              selection.addRange(range);
              handleInput();
              return;
            } else if (element.tagName === 'OL') {
              // Convert numbered list to bullet list
              const newLi = document.createElement('li');
              newLi.innerHTML = element.textContent || '<br>';
              const ul = document.createElement('ul');
              ul.appendChild(newLi);
              element.parentNode?.replaceChild(ul, element);
              range.setStart(newLi, 0);
              range.setEnd(newLi, 0);
              selection.removeAllRanges();
              selection.addRange(range);
              handleInput();
              return;
            }
          }
          container = container.parentNode;
        }
        
        // Get the current line content
        const currentLineContent = range.toString() || '';
        
        // Create bullet list with current content
        const ul = document.createElement('ul');
        const li = document.createElement('li');
        li.textContent = currentLineContent || '• ';
        ul.appendChild(li);
        
        // Replace current selection with the list
        range.deleteContents();
        range.insertNode(ul);
        
        // Position cursor at the end of the list item
        range.setStart(li, li.textContent?.length || 0);
        range.setEnd(li, li.textContent?.length || 0);
        selection.removeAllRanges();
        selection.addRange(range);
        handleInput();
      }
    }
  };

  const insertNumberedList = () => {
    if (editorRef.current) {
      editorRef.current.focus();
      
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        let container: Node | null = range.commonAncestorContainer;
        
        // Walk up the DOM tree to find if we're in a list
        while (container && container !== editorRef.current) {
          if (container.nodeType === Node.ELEMENT_NODE) {
            const element = container as Element;
            if (element.tagName === 'OL') {
              // Already in a numbered list, just add a new item
              const newLi = document.createElement('li');
              newLi.innerHTML = '<br>';
              range.insertNode(newLi);
              range.setStart(newLi, 0);
              range.setEnd(newLi, 0);
              selection.removeAllRanges();
              selection.addRange(range);
              handleInput();
              return;
            } else if (element.tagName === 'UL') {
              // Convert bullet list to numbered list
              const newLi = document.createElement('li');
              newLi.innerHTML = element.textContent || '<br>';
              const ol = document.createElement('ol');
              ol.appendChild(newLi);
              element.parentNode?.replaceChild(ol, element);
              range.setStart(newLi, 0);
              range.setEnd(newLi, 0);
              selection.removeAllRanges();
              selection.addRange(range);
              handleInput();
              return;
            }
          }
          container = container.parentNode;
        }
        
        // Get the current line content
        const currentLineContent = range.toString() || '';
        
        // Create numbered list with current content
        const ol = document.createElement('ol');
        const li = document.createElement('li');
        li.textContent = currentLineContent || '1. ';
        ol.appendChild(li);
        
        // Replace current selection with the list
        range.deleteContents();
        range.insertNode(ol);
        
        // Position cursor at the end of the list item
        range.setStart(li, li.textContent?.length || 0);
        range.setEnd(li, li.textContent?.length || 0);
        selection.removeAllRanges();
        selection.addRange(range);
        handleInput();
      }
    }
  };

  const toggleBold = () => {
    execCommand('bold');
  };

  const toggleItalic = () => {
    execCommand('italic');
  };

  const insertParagraph = () => {
    execCommand('insertParagraph');
  };

  return (
    <div className={`border border-gray-300 rounded-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent ${className}`}>
      {/* Toolbar */}
      <div className="flex items-center gap-1 p-2 border-b border-gray-200 bg-gray-50">
        <button
          type="button"
          onClick={toggleBold}
          className="p-1.5 rounded hover:bg-gray-200 transition-colors"
          title="Bold"
        >
          <Bold className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={toggleItalic}
          className="p-1.5 rounded hover:bg-gray-200 transition-colors"
          title="Italic"
        >
          <Italic className="h-4 w-4" />
        </button>
        <div className="w-px h-6 bg-gray-300 mx-1" />
        <button
          type="button"
          onClick={insertBulletList}
          className="p-1.5 rounded hover:bg-gray-200 transition-colors"
          title="Bullet List"
        >
          <List className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={insertNumberedList}
          className="p-1.5 rounded hover:bg-gray-200 transition-colors"
          title="Numbered List"
        >
          <Type className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={insertParagraph}
          className="p-1.5 rounded hover:bg-gray-200 transition-colors text-sm"
          title="New Paragraph"
        >
          ¶
        </button>
      </div>

      {/* Editor */}
      <div className="relative">
        <div
          ref={editorRef}
          contentEditable
          onInput={handleInput}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className="min-h-[200px] p-3 focus:outline-none bg-white"
          style={{
            lineHeight: '1.6',
            fontSize: '14px',
            direction: 'ltr',
            textAlign: 'left',
          }}
          suppressContentEditableWarning={true}
        />
        {!value && !isFocused && (
          <div className="absolute top-3 left-3 text-gray-400 pointer-events-none">
            {placeholder}
          </div>
        )}
      </div>


    </div>
  );
};

export default RichTextEditor;
