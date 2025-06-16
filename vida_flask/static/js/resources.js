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
                },
            });
        };
        self.refresh();
    }
}
var model = new ResourcesViewModel();
ko.applyBindings(model);
