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
        self.profileInfo = ko.observable({});

        if (self.selectedProfile()) {
            $.ajax({
                url: "/Vida/profiles",
                data: {
                    Id: self.selectedProfile(),
                },
                success: (resp) => self.profileInfo(resp),
            });
        }
    }
}
