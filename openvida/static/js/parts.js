function imgSize() {}

class PartsViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.component = ko.observable(ko.mapping.fromJS(COMPONENT));
        self.catalogue = ko.observableArray([]);

        self.layoutTemplate = () =>
            self.component().type() == 2 ? "panels" : "table";
        self.componentPath = (el) => `/parts/${el.path().replace(",", "/")}/`;
        self.attachmentPath = (el) =>
            el.attachment() ? `/Vida/img/${el.attachment()}` : null;

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
