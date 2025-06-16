class DocumentsViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.docsByQual = ko.observableArray();

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
            openLinkDoc(e.chronicleId);
        };

        window.addEventListener("popstate", function (e) {
            if (e.state == null) return;
            openLinkDoc(
                e.state.docId,
                e.state.isCallout,
                e.state.targetElement,
                e.state.sourceElement,
                e.state.isButton,
                true
            );
        });
    }
}
ko.applyBindings(new DocumentsViewModel());

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
                    window.location
                );
        },
    });
}

function openImage(imageURL, imgId) {
    window.open(imageURL, "image", "popup=true,width=400,height=400");
}

function imgSize(image) {}

function bigimgSize(image) {}
