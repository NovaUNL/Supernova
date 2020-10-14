MathJax = {
    options: {
        ignoreHtmlClass: 'tex2jax_ignore',
        processHtmlClass: 'tex2jax_process',
        renderActions: {
            find: [10, function (doc) {
                for (const node of document.querySelectorAll('script[type^="math/tex"]')) {
                    const display = !!node.type.match(/; *mode=display/);
                    const math = new doc.options.MathItem(node.textContent, doc.inputJax[0], display);
                    const text = document.createTextNode('');
                    const sibling = node.previousElementSibling;
                    node.parentNode.replaceChild(text, node);
                    math.start = {node: text, delim: '', n: 0};
                    math.end = {node: text, delim: '', n: 0};
                    doc.math.push(math);
                    if (sibling && sibling.matches('.MathJax_Preview')) {
                        sibling.parentNode.removeChild(sibling);
                    }
                }
            }, '']
        }
    }
};

function setupMarkdownEnv() {
    let element = document.querySelectorAll('.markdownx');
    Object.keys(element).map(key =>
        element[key].addEventListener('markdownx.update', event => {
            MathJax.typeset();
            Prism.highlightAll();
        })
    );
    MathJax.typeset();
    Prism.highlightAll();
}


function toggleMarkdownPreview(e, state) {
    let root = e.closest(".markdown-editor");
    let preview = root.querySelector(".preview");
    let editor = root.querySelector("textarea");
    let previewBtn = root.querySelector(".preview-btn");
    let editBtn = root.querySelector(".edit-btn");
    if (state) {
        editor.style.display = "none";
        preview.style.display = "block";
        previewBtn.classList.add("selected");
        editBtn.classList.remove("selected");
    } else {
        editor.style.display = "block";
        preview.style.display = "none";
        previewBtn.classList.remove("selected");
        editBtn.classList.add("selected");
    }
}