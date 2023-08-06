import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { FileEditor, IEditorTracker } from '@jupyterlab/fileeditor';

import { INotebookTracker } from '@jupyterlab/notebook';

import { LabIcon } from '@jupyterlab/ui-components';

import { ICommandPalette } from '@jupyterlab/apputils';

import { Menu } from '@lumino/widgets';

import '../style/index.css';

import * as CodeMirror from 'codemirror';

import spellcheckSvg from '../style/icons/ic-baseline-spellcheck.svg';
import { Cell } from '@jupyterlab/cells';

export const spellcheckIcon = new LabIcon({
  name: 'spellcheck:spellcheck',
  svgstr: spellcheckSvg
});

declare function require(name: string): any;
let Typo = require('typo-js');

const CMD_TOGGLE = 'spellchecker:toggle-check-spelling';
const CMD_APPLY_SUGGESTION = 'spellchecker:apply-suggestion';

/**
 * SpellChecker
 */
class SpellChecker {
  dictionary: any;
  dict_promise: any;
  app: JupyterFrontEnd;
  tracker: INotebookTracker;
  palette: ICommandPalette;
  editor_tracker: IEditorTracker;
  suggestions_menu: Menu;

  // Default Options
  check_spelling: boolean = true;
  aff_url: string =
    'https://cdn.jsdelivr.net/codemirror.spell-checker/latest/en_US.aff';
  dict_url: string =
    'https://cdn.jsdelivr.net/codemirror.spell-checker/latest/en_US.dic';
  lang_code: string = 'en_Us';
  rx_word_char: RegExp = /[^-\[\]{}():\/!;&@$£%§<>"*+=?.,~\\^|_`#±\s\t]/;
  rx_non_word_char: RegExp = /[-\[\]{}():\/!;&@$£%§<>"*+=?.,~\\^|_`#±\s\t]/;
  accepted_types = [
    'text/plain',
    'text/x-ipythongfm' // IPython GFM = GitHub Flavored Markdown, applies to all .md files
  ];

  constructor(
    app: JupyterFrontEnd,
    notebook_tracker: INotebookTracker,
    palette: ICommandPalette,
    editor_tracker: IEditorTracker
  ) {
    this.app = app;
    this.tracker = notebook_tracker;
    this.editor_tracker = editor_tracker;
    this.palette = palette;
    this.setup_button();
    this.setup_suggestions();
    this.load_dictionary();
    this.tracker.activeCellChanged.connect(this.onActiveCellChanged, this);

    this.editor_tracker.widgetAdded.connect((sender, widget) => {
      let file_editor = widget.content;

      if (this.accepted_types.indexOf(file_editor.model.mimeType) !== -1) {
        let editor = this.extract_editor(file_editor);
        this.setup_overlay(editor);
      }
    });
  }

  onActiveCellChanged(): void {
    let active_cell = this.tracker.activeCell;

    if (active_cell !== null && active_cell.model.type == 'markdown') {
      let editor = this.extract_editor(active_cell);
      this.setup_overlay(editor);
    }
  }

  extract_editor(cell_or_editor: Cell | FileEditor): CodeMirror.Editor {
    let editor_temp = cell_or_editor.editor;
    // @ts-ignore
    return editor_temp._editor;
  }

  setup_overlay(editor: CodeMirror.Editor, retry = true): void {
    let current_mode = editor.getOption('mode') as string;

    if (current_mode == 'null') {
      if (retry) {
        setTimeout(() => this.setup_overlay(editor, false), 0);
      }
      return;
    }

    if (this.check_spelling) {
      editor.setOption('mode', this.define_mode(current_mode));
    } else {
      let original_mode = current_mode.match(/^spellcheck_/)
        ? current_mode.substr(11)
        : current_mode;
      editor.setOption('mode', original_mode);
    }
  }

  toggle_spellcheck() {
    this.check_spelling = !this.check_spelling;
    console.log('Spell checking is currently: ', this.check_spelling);
  }

  setup_button() {
    this.app.commands.addCommand(CMD_TOGGLE, {
      label: 'Check Spelling',
      execute: () => {
        this.toggle_spellcheck();
      }
    });
    this.palette.addItem({
      command: CMD_TOGGLE,
      category: 'Toggle Spell Checker'
    });
  }

  setup_suggestions() {
    this.suggestions_menu = new Menu({ commands: this.app.commands });
    this.suggestions_menu.title.label = 'Spellcheck suggestions';
    this.suggestions_menu.title.icon = spellcheckIcon.bindprops({
      stylesheet: 'menuItem'
    });
    let CMD_UPDATE_SUGGESTIONS = 'spellchecker:update-suggestions';

    this.app.commands.addCommand(CMD_UPDATE_SUGGESTIONS, {
      execute: args => {},
      isVisible: args => {
        // This command is not meant to be show - it is just menu trigger detection hack
        let widget =
          this.tracker.activeCell || this.editor_tracker.currentWidget.content;
        let position = widget.editor.getCursorPosition();

        let code_mirror = this.extract_editor(widget);
        let mode = code_mirror.getModeAt({
          ch: position.column,
          line: position.line
        });
        console.log(mode);
        console.log(code_mirror.getLineTokens(position.line));

        let token = widget.editor.getTokenForPosition(position);
        let text = token.value;
        console.log(text);
        let suggestions: string[] = this.dictionary.suggest(text);
        this.suggestions_menu.clearItems();
        for (let suggestion of suggestions) {
          this.suggestions_menu.addItem({
            command: CMD_APPLY_SUGGESTION,
            args: { name: suggestion }
          });
        }
        return false;
      }
    });
    this.app.contextMenu.addItem({
      selector: '.cm-spell-error',
      command: CMD_UPDATE_SUGGESTIONS
    });
    this.app.contextMenu.addItem({
      selector: '.cm-spell-error',
      submenu: this.suggestions_menu,
      type: 'submenu'
    });
    this.app.commands.addCommand(CMD_APPLY_SUGGESTION, {
      execute: args => {
        //this.selected_token.innerText = args['name'] as string;
        let widget =
          this.tracker.activeCell || this.editor_tracker.currentWidget.content;
        let position = widget.editor.getCursorPosition();
        let code_mirror = this.extract_editor(widget);
        console.log(code_mirror.getLineTokens(position.line));

        let code_mirror_token = code_mirror.getTokenAt({
          ch: position.column,
          line: position.line
        });
        code_mirror.getDoc().replaceRange(
          args['name'] as string,
          {
            ch: code_mirror_token.start,
            line: position.line
          },
          {
            ch: code_mirror_token.end,
            line: position.line
          }
        );
      },
      label: args => args['name'] as string,
      isVisible: () => {
        return true;
      }
    });
  }

  load_dictionary() {
    this.dict_promise = Promise.all([
      fetch(this.aff_url).then(res => res.text()),
      fetch(this.dict_url).then(res => res.text())
    ]).then(values => {
      this.dictionary = new Typo(this.lang_code, values[0], values[1]);
      console.log('Dictionary Loaded ', this.lang_code);
    });
  }

  /*
    update_suggestions() {
        for (let column of panel_widget.content.columns) {
        }
    }
     */

  define_mode = (original_mode_spec: string) => {
    if (original_mode_spec.indexOf('spellcheck_') == 0) {
      return original_mode_spec;
    }
    var me = this;
    var new_mode_spec = 'spellcheck_' + original_mode_spec;
    CodeMirror.defineMode(new_mode_spec, (config: any) => {
      var spellchecker_overlay = {
        name: new_mode_spec,
        token: function (stream: any, state: any) {
          let base_token = stream.baseToken() as CodeMirror.Token;
          console.log(base_token);
          stream.next();
        }
      };
      return CodeMirror.overlayMode(
        CodeMirror.getMode(config, original_mode_spec),
        spellchecker_overlay,
        true
      );
    });
    return new_mode_spec;
  };
}

/**
 * Activate extension
 */
function activate(
  app: JupyterFrontEnd,
  tracker: INotebookTracker,
  palette: ICommandPalette,
  editor_tracker: IEditorTracker
) {
  console.log('Attempting to load spellchecker');
  const sp = new SpellChecker(app, tracker, palette, editor_tracker);
  console.log('Spellchecker Loaded ', sp);
}

/**
 * Initialization data for the jupyterlab_spellchecker extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_spellchecker',
  autoStart: true,
  requires: [INotebookTracker, ICommandPalette, IEditorTracker],
  activate: activate
};

export default extension;
