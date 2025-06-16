class VidaBaseModel {
    constructor() {
        var self = this;

        self.selectedProfile = ko.observable(
            sessionStorage.getItem("selectedProfile")
        );
        self.selectedProfile.subscribe((v) => {
            sessionStorage.setItem("selectedProfile", v);
            self.refreshDocs();
        });
    }
}
