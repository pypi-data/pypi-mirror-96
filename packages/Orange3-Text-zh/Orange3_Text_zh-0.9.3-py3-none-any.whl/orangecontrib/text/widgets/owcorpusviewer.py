import re
import sre_constants
from itertools import chain

from AnyQt.QtCore import (
    Qt, QUrl, QItemSelection, QItemSelectionModel, QItemSelectionRange
)

from AnyQt.QtGui import QStandardItemModel, QStandardItem
from AnyQt.QtWidgets import (QListView, QSizePolicy, QTableView,
                             QAbstractItemView, QHeaderView, QSplitter,
                             QApplication)

from Orange.data.domain import filter_visible
from Orange.widgets import gui
from Orange.widgets.settings import Setting, ContextSetting, PerfectDomainContextHandler
from Orange.widgets.widget import OWWidget, Msg, Input, Output
from orangecontrib.text.corpus import Corpus


class OWCorpusViewer(OWWidget):
    name = "语料查看器(Corpus Viewer)"
    description = "显示语料库内容."
    icon = "icons/CorpusViewer.svg"
    priority = 500

    class Inputs:
        corpus = Input("语料库(Corpus)", Corpus, replaces=["Data", 'Corpus'])

    class Outputs:
        matching_docs = Output("匹配的文档(Matching Docs)", Corpus, default=True, replaces=['Matching Docs'])
        other_docs = Output("其他文档(Other Docs)", Corpus, replaces=['Corpus'])

    settingsHandler = PerfectDomainContextHandler(
        match_values = PerfectDomainContextHandler.MATCH_VALUES_ALL
    )

    search_indices = ContextSetting([], exclude_metas=False)   # features included in search
    display_indices = ContextSetting([], exclude_metas=False)  # features for display
    display_features = ContextSetting([], exclude_metas=False)
    regexp_filter = ContextSetting("")

    selection = [0]  # TODO: DataHashContextHandler

    show_tokens = Setting(False)
    autocommit = Setting(True)

    class Warning(OWWidget.Warning):
        no_feats_search = Msg('搜索中没有特征')
        no_feats_display = Msg('没有选中要显示的特征.')

    def __init__(self):
        super().__init__()

        self.corpus = None              # Corpus
        self.corpus_docs = None         # Documents generated from Corpus
        self.output_mask = []           # Output corpus indices
        self.doc_webview = None         # WebView for showing content
        self.search_features = []       # two copies are needed since Display allows drag & drop
        self.display_list_indices = [0]

        # Info attributes
        self.update_info()
        info_box = gui.widgetBox(self.controlArea, '信息')
        gui.label(info_box, self, '文档: %(n_documents)s')
        gui.label(info_box, self, '预处: %(is_preprocessed)s')
        gui.label(info_box, self, '  ◦ 词(Token): %(n_tokens)s')
        gui.label(info_box, self, '  ◦ : %(n_types)s')
        gui.label(info_box, self, 'POS 标签: %(is_pos_tagged)s')
        gui.label(info_box, self, 'N-grams 范围: %(ngram_range)s')
        gui.label(info_box, self, '匹配: %(n_matching)s')

        # Search features
        self.search_listbox = gui.listBox(
            self.controlArea, self, 'search_indices', 'search_features',
            selectionMode=QListView.ExtendedSelection,
            box='搜索特征', callback=self.search_features_changed)

        # Display features
        display_box = gui.widgetBox(self.controlArea, '显示特征')
        self.display_listbox = gui.listBox(
            display_box, self, 'display_list_indices', 'display_features',
            selectionMode=QListView.ExtendedSelection,
            callback=self.show_docs, enableDragDrop=True)
        self.show_tokens_checkbox = gui.checkBox(display_box, self, 'show_tokens',
                                                 '显示词和标签', callback=self.show_docs)

        # Auto-commit box
        gui.auto_commit(self.controlArea, self, 'autocommit', '发送数据', '自动发送已开')

        # Search
        self.filter_input = gui.lineEdit(self.mainArea, self, 'regexp_filter',
                                         orientation=Qt.Horizontal,
                                         sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                                                QSizePolicy.Fixed),
                                         label='正则表达式筛选:')
        self.filter_input.textChanged.connect(self.refresh_search)

        # Main area
        self.splitter = QSplitter(
            orientation=Qt.Horizontal,
            childrenCollapsible=False,
        )

        # Document list
        self.doc_list = QTableView()
        self.doc_list.setSelectionBehavior(QTableView.SelectRows)
        self.doc_list.setSelectionMode(QTableView.ExtendedSelection)
        self.doc_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.doc_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.doc_list.horizontalHeader().setVisible(False)
        self.splitter.addWidget(self.doc_list)

        self.doc_list_model = QStandardItemModel(self)
        self.doc_list.setModel(self.doc_list_model)
        self.doc_list.selectionModel().selectionChanged.connect(self.show_docs)

        # Document contents
        self.doc_webview = gui.WebviewWidget(self.splitter, debug=False)

        self.mainArea.layout().addWidget(self.splitter)

    def copy_to_clipboard(self):
        text = self.doc_webview.selectedText()
        QApplication.clipboard().setText(text)

    @Inputs.corpus
    def set_data(self, corpus=None):
        self.closeContext()
        self.reset_widget()
        self.corpus = corpus
        self.search_features = []
        if corpus is not None:
            domain = self.corpus.domain
            # Enable/disable tokens checkbox
            if not self.corpus.has_tokens():
                self.show_tokens_checkbox.setCheckState(False)
            self.show_tokens_checkbox.setEnabled(self.corpus.has_tokens())

            self.search_features = list(filter_visible(chain(domain.variables, domain.metas)))
            self.display_features = list(filter_visible(chain(domain.variables, domain.metas)))
            self.search_indices = list(range(len(self.search_features)))
            self.display_indices = list(range(len(self.display_features)))
            self.selection = [0]
            self.openContext(self.corpus)
            self.display_list_indices = self.display_indices
            self.regenerate_docs()
            self.list_docs()
            self.update_info()
            self.set_selection()
            self.show_docs()
        self.commit()

    def reset_widget(self):
        # Corpus
        self.corpus = None
        self.corpus_docs = None
        self.output_mask = []
        self.display_features = []
        # Widgets
        self.search_listbox.clear()
        self.display_listbox.clear()
        self.filter_input.clear()
        self.update_info()
        # Models/vars
        self.search_features.clear()
        self.search_indices.clear()
        self.display_indices.clear()
        self.doc_list_model.clear()
        # Warnings
        self.Warning.clear()
        # WebView
        self.doc_webview.setHtml('')

    def list_docs(self):
        """ List documents into the left scrolling area """
        if self.corpus_docs is None:
            return
        search_keyword = self.regexp_filter.strip('|')
        try:
            reg = re.compile(search_keyword, re.IGNORECASE)
        except sre_constants.error:
            return

        def is_match(x):
            return not bool(search_keyword) or reg.search(x)

        self.output_mask.clear()
        self.doc_list_model.clear()

        for i, (doc, title, content) in enumerate(zip(self.corpus, self.corpus.titles,
                                                      self.corpus_docs)):
            if is_match(content):
                item = QStandardItem()
                item.setData(title, Qt.DisplayRole)
                item.setData(doc, Qt.UserRole)
                self.doc_list_model.appendRow(item)
                self.output_mask.append(i)

    def reset_selection(self):
        if self.doc_list_model.rowCount() > 0:
            self.doc_list.selectRow(0)  # Select the first document
        else:
            self.doc_webview.setHtml('')

    def set_selection(self):
        view = self.doc_list
        if len(self.selection):
            selection = QItemSelection()

            for row in self.selection:
                selection.append(
                    QItemSelectionRange(
                        view.model().index(row, 0),
                        view.model().index(row, 0)
                    )
                )
            view.selectionModel().select(
                selection, QItemSelectionModel.ClearAndSelect)

    def show_docs(self):
        """ Show the selected documents in the right area """
        HTML = '''
        <!doctype html>
        <html>
        <head>
        <script type="text/javascript" src="resources/jquery-3.1.1.min.js">
        </script>
        <script type="text/javascript" src="resources/jquery.mark.min.js">
        </script>
        <script type="text/javascript" src="resources/highlighter.js">
        </script>
        <meta charset='utf-8'>
        <style>

        table {{ border-collapse: collapse; }}
        mark {{ background: #FFCD28; }}

        tr > td {{
            padding-bottom: 3px;
            padding-top: 3px;
        }}

        body {{
            font-family: Helvetica;
            font-size: 10pt;
        }}

        .line {{ border-bottom: 1px solid #000; }}
        .separator {{ height: 5px; }}

        .variables {{
            vertical-align: top;
            padding-right: 10px;
        }}
        
        .content {{
            /* Adopted from https://css-tricks.com/snippets/css/prevent-long-urls-from-breaking-out-of-container/ */
        
            /* These are technically the same, but use both */
            overflow-wrap: break-word;
            word-wrap: break-word;
        
            -ms-word-break: break-all;
            /* This is the dangerous one in WebKit, as it breaks things wherever */
            word-break: break-all;
            /* Instead use this non-standard one: */
            word-break: break-word;
        
            /* Adds a hyphen where the word breaks, if supported (No Blink) */
            -ms-hyphens: auto;
            -moz-hyphens: auto;
            -webkit-hyphens: auto;
            hyphens: auto;
        }}

        .token {{
            padding: 3px;
            border: 1px #B0B0B0 solid;
            margin-right: 5px;
            margin-bottom: 5px;
            display: inline-block;
        }}

        img {{
            max-width: 100%;
        }}

        </style>
        </head>
        <body>
        {}
        </body>
        </html>
        '''
        self.display_indices = self.display_list_indices
        if self.corpus is None:
            return

        self.Warning.no_feats_display.clear()
        if len(self.display_indices) == 0:
            self.Warning.no_feats_display()

        if self.show_tokens:
            tokens = list(self.corpus.ngrams_iterator(include_postags=True))

        marked_search_features = [f for i, f in enumerate(self.search_features)
                                  if i in self.search_indices]

        html = '<table>'
        selection = [i.row() for i in self.doc_list.selectionModel().selectedRows()]
        if selection != []:
            self.selection = selection
        for doc_count, index in enumerate(self.doc_list.selectionModel().selectedRows()):
            if doc_count > 0:   # add split
                html += '<tr class="line separator"><td/><td/></tr>' \
                        '<tr class="separator"><td/><td/></tr>'

            row_ind = index.data(Qt.UserRole).row_index
            for ind in self.display_indices:
                feature = self.display_features[ind]
                value = str(index.data(Qt.UserRole)[feature.name])
                if feature in marked_search_features:
                    value = self.__mark_text(value)
                value = value.replace('\n', '<br/>')
                is_image = feature.attributes.get('type', '') == 'image'
                if is_image and value != '?':
                    value = '<img src="{}"></img>'.format(value)
                html += '<tr><td class="variables"><strong>{}:</strong></td>' \
                        '<td class="content">{}</td></tr>'.format(
                    feature.name, value)

            if self.show_tokens:
                html += '<tr><td class="variables"><strong>Tokens & Tags:</strong></td>' \
                        '<td>{}</td></tr>'.format(''.join('<span class="token">{}</span>'.format(
                    token) for token in tokens[row_ind]))

        html += '</table>'
        base = QUrl.fromLocalFile(__file__)
        self.doc_webview.setHtml(HTML.format(html), base)

    def __mark_text(self, text):
        search_keyword = self.regexp_filter.strip('|')
        if not search_keyword:
            return text

        try:
            reg = re.compile(search_keyword, re.IGNORECASE | re.MULTILINE)
        except sre_constants.error:
            return text

        matches = list(reg.finditer(text))
        if not matches:
            return text

        text = list(text)
        for m in matches[::-1]:
            text[m.start():m.end()] = list('<mark data-markjs="true">{}</mark>'\
                .format("".join(text[m.start():m.end()])))

        return "".join(text)

    def search_features_changed(self):
        self.regenerate_docs()
        self.refresh_search()

    def regenerate_docs(self):
        self.corpus_docs = None
        self.Warning.no_feats_search.clear()
        if self.corpus is not None:
            feats = [self.search_features[i] for i in self.search_indices]
            if len(feats) == 0:
                self.Warning.no_feats_search()
            self.corpus_docs = self.corpus.documents_from_features(feats)

    def refresh_search(self):
        if self.corpus is not None:
            self.list_docs()
            self.reset_selection()
            self.update_info()
            self.commit()

    def update_info(self):
        if self.corpus is not None:
            self.n_documents = len(self.corpus)
            self.n_matching = '{}/{}'.format(self.doc_list_model.rowCount(), self.n_documents)
            self.n_tokens = sum(map(len, self.corpus.tokens)) if self.corpus.has_tokens() else 'n/a'
            self.n_types = len(self.corpus.dictionary) if self.corpus.has_tokens() else 'n/a'
            self.is_preprocessed = self.corpus.has_tokens()
            self.is_pos_tagged = self.corpus.pos_tags is not None
            self.ngram_range = '{}-{}'.format(*self.corpus.ngram_range)
        else:
            self.n_documents = ''
            self.n_matching = ''
            self.n_tokens = ''
            self.n_types = ''
            self.is_preprocessed = ''
            self.is_pos_tagged = ''
            self.ngram_range = ''

    def commit(self):
        if self.corpus is not None:
            matched = self.corpus[self.output_mask]
            output_mask = set(self.output_mask)
            unmatched_mask = [i for i in range(len(self.corpus)) if i not in output_mask]
            unmatched = self.corpus[unmatched_mask]
            self.Outputs.matching_docs.send(matched)
            self.Outputs.other_docs.send(unmatched)
        else:
            self.Outputs.matching_docs.send(None)
            self.Outputs.other_docs.send(None)

    def send_report(self):
        self.report_items((
            ("Query", self.regexp_filter),
            ("Matching documents", self.n_matching),
        ))


if __name__ == '__main__':
    from orangecontrib.text.tag.pos import AveragedPerceptronTagger
    app = QApplication([])
    widget = OWCorpusViewer()
    widget.show()
    corpus = Corpus.from_file('book-excerpts')
    corpus = corpus[:3]
    tagger = AveragedPerceptronTagger()
    tagged_corpus = tagger.tag_corpus(corpus)
    tagged_corpus.ngram_range = (1, 2)
    widget.set_data(tagged_corpus)
    app.exec()
