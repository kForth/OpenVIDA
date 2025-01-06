class VidaModel {
    constructor() {
        var self = this;

        self.market = ko.observable();
        self.modelYear = ko.observable();
        self.model = ko.observable();
        self.engine = ko.observable();
        self.transmission = ko.observable();
        self.steering = ko.observable();
        self.bodyStyle = ko.observable();
        self.specialVehicle = ko.observable();

        self.marketOptions = ko.observableArray();
        self.modelYearOptions = ko.observableArray();
        self.modelOptions = ko.observableArray();
        self.engineOptions = ko.observableArray();
        self.transmissionOptions = ko.observableArray();
        self.steeringOptions = ko.observableArray();
        self.bodyStyleOptions = ko.observableArray();
        self.specialVehicleOptions = ko.observableArray();
        self.profiles = ko.observableArray();

        $.get("/vida/markets").then((e) => self.marketOptions(e));
        $.get("/vida/modelYears").then((e) => self.modelYearOptions(e));
        $.get("/vida/models").then((e) => self.modelOptions(e));
        $.get("/vida/engines").then((e) => self.engineOptions(e));
        $.get("/vida/transmissions").then((e) => self.transmissionOptions(e));
        $.get("/vida/steerings").then((e) => self.steeringOptions(e));
        $.get("/vida/bodyStyles").then((e) => self.bodyStyleOptions(e));
        $.get("/vida/specialVehicles").then((e) => self.specialVehicleOptions(e));
        $.get("/vida/profiles").then((e) => { self.profiles(e) });
    }
}

var model = new VidaModel();
ko.applyBindings(model);
