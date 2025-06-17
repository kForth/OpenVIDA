function imgSize() {}

class PartsViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.partsTree = ko.observableArray([]);
        self.selectedCatalogue = ko.observableArray([]);

        self.nodeTemplate = (e) => (e.type() == 2 ? "node" : "link");
        self.nodeTitle = (e) =>
            `${e.id().toString().padEnd(4, "\u00a0")} ${e.description()}`;
        self.linkTitle = (e) =>
            e.note() ? `${e.description()} - ${e.note()}` : e.description();

        self.refreshParts = function () {
            $.ajax({
                url: `/Vida/epc/topLevelToc/`,
                data: { selectedProfile: self.selectedProfile() },
                success: (resp) => {
                    var tree = [];
                    for (let e of resp) {
                        let obj = ko.mapping.fromJS(e);
                        obj.children = ko.observableArray([]);
                        tree.push(obj);
                    }
                    self.partsTree(tree);
                },
            });
        };

        self.loadChildren = function (e) {
            if (e.children.length) return;
            $.ajax({
                url: "/Vida/epc/getTocElements",
                data: {
                    selectedProfile: self.selectedProfile(),
                    parentId: e.id(),
                    assemblyLevel: e.assemblyLevel(),
                },
                success: (resp) => {
                    let children = [];
                    for (let e of resp) {
                        let obj = ko.mapping.fromJS(e);
                        obj.children = ko.observableArray([]);
                        children.push(obj);
                    }
                    e.children(children);
                },
            });
        };

        self.selectComponent = function (e) {
            self.selectedCatalogue([]);
            $.ajax({
                url: "/Vida/epc/getParts",
                data: { parentId: e.id() },
                success: (resp) => self.selectedCatalogue(resp),
            });
        };

        // Util
        self.pushAll = (a1, a2) => a2.forEach((e) => a1.push(ko.observable(e)));

        self.refreshParts();
    }
}
ko.applyBindings(new PartsViewModel());
