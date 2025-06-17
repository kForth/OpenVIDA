class VidaBaseModel {
    constructor() {
        var self = this;

        self.selectedProfile = ko.observable(
            sessionStorage.getItem("selectedProfile")
        );
        self.selectedProfile.subscribe((v) => {
            sessionStorage.setItem("selectedProfile", v);
        });
        self.profileInfo = ko.observable({});

        if (self.selectedProfile()) {
            $.ajax({
                url: "/Vida/profile",
                data: {
                    Id: self.selectedProfile(),
                },
                success: (resp) => self.profileInfo(resp),
            });
        }
    }
}
