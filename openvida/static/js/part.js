class PartViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.component = ko.observable(ko.mapping.fromJS(PART));
        self.sources = ko.observableArray([
            { title: "VolvoCars.com", href: (item) => `https://usparts.volvocars.com/p/${item}.html` },
            { title: "VolvoCars.ca", href: (item) => `https://parts.volvocars.ca/p/${item}.html` },
            { title: "Toronto Volvo", href: (item) => `https://www.volvocarstorontoparts.ca/p/${item}.html` },
            { title: "Hamilton Volvo", href: (item) => `https://parts.volvocarshamilton.com/p/${item}.html` },
            { title: "FCP Euro", href: (item) => `https://www.fcpeuro.com/Volvo-parts?keywords=${item}` },
        ]);

        $.ajax()
    }
}
var model = new PartViewModel();
ko.applyBindings(model);
