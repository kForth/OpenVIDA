class ResourcesViewModel {
    constructor() {
        var self = this;

        self.selectedProfile = ko.observable(
            sessionStorage.getItem("selectedProfile")
        );
        self.selectedProfile.subscribe((v) => {
            sessionStorage.setItem("selectedProfile", v);
            self.refresh();
        });

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
