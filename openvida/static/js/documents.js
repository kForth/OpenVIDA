class DocumentsViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.docsByQual = ko.observableArray();
        self.docSearchStr = ko.observable("");

        self.activeDoc = ko.observable(ko.mapping.fromJS(INITIAL_DOCUMENT));
        function loadDocById(docId) {
            $.ajax({
                url: `/Vida/document/html/${docId}`,
                method: "get",
                success: (resp) => self.activeDoc(ko.mapping.fromJS(resp)),
            })
        }
        self.activeDocId = ko.computed(() => self.activeDoc().chronicleId());
        self.activeDocLink = ko.computed(() => self.activeDocId() ? `/document/${self.activeDocId()}/` : '#');

        self.filteredDocsByQual = ko.pureComputed(function () {
            const query = (self.docSearchStr() || "").trim().toLowerCase();
            if (!query) return self.docsByQual();

            return self.docsByQual()
                .map((group) => {
                    const docs = (group.docs || []).filter((doc) =>
                        (doc.title || "").toLowerCase().includes(query)
                    );

                    return docs.length > 0 ? { ...group, docs: docs } : null;
                })
                .filter(Boolean);
        });

        self.refreshDocs = function () {
            $.ajax({
                url: `/Vida/docsByQual/${self.selectedProfile()}?qualCols=id,title&docCols=id,chronicleId,fkQualifier,title`,
                method: "get",
                success: (resp) => {
                    self.docsByQual(resp);
                },
            });
        };
        self.refreshDocs();

        self.selectDocument = function (e) {
            self.activeDoc(ko.mapping.fromJS(e));
            openLinkDoc(e.chronicleId);
        };

        window.addEventListener("popstate", function (e) {
            if (e.state == null) {
                const pathDocId = getDocumentIdFromPath();
                loadDocById(pathDocId);
                // self.activeDocId(pathDocId);
                if (pathDocId) {
                    openLinkDoc(pathDocId, null, null, null, null, true);
                }
                return;
            }

            loadDocById(e.state.docId);
            // self.activeDocId(e.state.docId || null);
            openLinkDoc(
                e.state.docId,
                e.state.isCallout,
                e.state.targetElement,
                e.state.sourceElement,
                e.state.isButton,
                true
            );
        });

        // Load initial document, if it exists
        if (self.activeDocId())
            openLinkDoc(self.activeDocId(), null, null, null, null, true);
    }
}
ko.applyBindings(new DocumentsViewModel());

function getDocumentIdFromPath() {
    const match = window.location.pathname.match(/^\/documents\/([^/]+)\/?$/);
    return match ? decodeURIComponent(match[1]) : null;
}

function getDocumentsPath(docId) {
    return docId ? `/documents/${encodeURIComponent(docId)}/` : "/documents/";
}

function openLinkDoc(
    docId,
    isCallout,
    targetElement,
    sourceElement,
    isButton,
    noHistory
) {
    var url;
    if (docId != null && docId.length != 0) {
        url = `/Vida/document/html/${docId}`;
    } else if (sourceElement != null && sourceElement.length != 0) {
        url = `/Vida/doclink/${sourceElement}`;
    } else return;

    $.ajax({
        url: url,
        method: "GET",
        success: (resp) => {
            $("#docContent").html(resp);
            if (!noHistory)
                window.history.pushState(
                    {
                        docId: docId,
                        isCallout: isCallout,
                        targetElement: targetElement,
                        sourceElement: sourceElement,
                        isButton: isButton,
                    },
                    undefined,
                    getDocumentsPath(docId)
                );
        },
    });
}

function openImage(imageURL, imgId) {
    window.open(imageURL, "image", "popup=true,width=400,height=400");
}

function imgSize(image) {}

function bigimgSize(image) {}
