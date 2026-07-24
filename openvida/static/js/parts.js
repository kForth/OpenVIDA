class PartsViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.component = ko.observable(ko.mapping.fromJS(COMPONENT));
        self.catalogue = ko.observableArray([]);

        self.layoutTemplate = function () {
            const component = self.component();
            return component.type() == 3 ? "table" :
                   component.assemblyLevel() == 2 ? "panels" :
                   "blocks";
        }
        self.componentPath = function (el) {
            return `/parts/${el.path().replace(",", "/")}/`;
        }
        self.attachmentPath = function (el) {
            return el.attachment() ? `/Vida/img/${el.attachment()}` : null;
        }
        self.showDiagramModal = function () {
            if (self.attachmentPath(self.component()))
                bootstrap.Modal.getOrCreateInstance(document.getElementById("diagramModal")).show();
        }

        // Load component list for current catalogue
        $.ajax({
            url: "/Vida/epc/getComponents",
            data: {
                path: COMPONENT_PATH,
                selectedProfile: self.selectedProfile(),
            },
            success: (resp) =>
                self.catalogue(resp.map((e) => ko.mapping.fromJS(e))),
        });
    }
}
var model = new PartsViewModel();
ko.applyBindings(model);
