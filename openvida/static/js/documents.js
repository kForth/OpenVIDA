class DocumentsViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.docsByQual = ko.observableArray();
        self.documentSearch = ko.observable("");
        self.selectedDocumentId = ko.observable(null);

        self.filteredDocsByQual = ko.pureComputed(function () {
            const query = (self.documentSearch() || "").trim().toLowerCase();
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
            self.selectedDocumentId(e.chronicleId);
            openLinkDoc(e.chronicleId);
        };

        window.addEventListener("popstate", function (e) {
            if (e.state == null) {
                const pathDocId = getDocumentIdFromPath();
                self.selectedDocumentId(pathDocId);
                if (pathDocId) {
                    openLinkDoc(pathDocId, null, null, null, null, true);
                }
                return;
            }

            self.selectedDocumentId(e.state.docId || null);
            openLinkDoc(
                e.state.docId,
                e.state.isCallout,
                e.state.targetElement,
                e.state.sourceElement,
                e.state.isButton,
                true
            );
        });

        if (INITIAL_CHRONICLE) {
            self.selectedDocumentId(INITIAL_CHRONICLE);
            openLinkDoc(INITIAL_CHRONICLE, null, null, null, null, true);
            window.history.replaceState(
                {
                    docId: INITIAL_CHRONICLE,
                    isCallout: null,
                    targetElement: null,
                    sourceElement: null,
                    isButton: null,
                },
                undefined,
                getDocumentsPath(INITIAL_CHRONICLE)
            );
        }
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
        url = `/Vida/document/${docId}`;
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
