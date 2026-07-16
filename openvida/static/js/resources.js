class ResourcesViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.resources = ko.observableArray();
        self.selectedResourcePath = ko.observable("about:blank");

        self.refresh = function () {
            $.ajax({
                url: "/Vida/resources/",
                method: "get",
                success: (resp) => {
                    self.resources(resp);
                    if (resp && resp.length > 0 && !self.selectedResourcePath()) {
                        self.selectedResourcePath(resp[0].url);
                    }
                },
            });
        };
        self.refresh();
    }
}
var model = new ResourcesViewModel();
ko.applyBindings(model);
