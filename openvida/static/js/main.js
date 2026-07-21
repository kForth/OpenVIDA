const selectedProfileKey = "selectedProfile";

function readCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
    return null;
}

function writeCookie (name, value, maxAgeSeconds = 2592000) {
    document.cookie = `${name}=${encodeURIComponent(value)}; Path=/; Max-Age=${maxAgeSeconds}; SameSite=Lax`;
}

function clearCookie (name) {
    document.cookie = `${name}=; Path=/; Max-Age=0; SameSite=Lax`;
}

function getProfileCookie () {
    const fromCookie = readCookie(selectedProfileKey);
    if (fromCookie) return decodeURIComponent(fromCookie);
    return localStorage.getItem(selectedProfileKey);
}

function setProfileCookie (value) {
    const normalizedValue = value === null || value === undefined ? "" : String(value).trim();
    if (!normalizedValue) {
        localStorage.removeItem(selectedProfileKey);
        clearCookie(selectedProfileKey);
        return;
    }
    localStorage.setItem(selectedProfileKey, normalizedValue);
    writeCookie(selectedProfileKey, normalizedValue);
}

class VidaBaseModel {
    constructor() {
        var self = this;

        self.selectedProfile = ko.observable(getProfileCookie());
        self.profileInfo = ko.observable({});

        self.loadProfileInfo = function () {
            if (!self.selectedProfile()) {
                self.profileInfo({});
                return;
            }
            $.ajax({
                url: "/Vida/profile",
                data: {Id: self.selectedProfile()},
                success: (resp) => self.profileInfo(resp),
            });
        };

        self.selectedProfile.subscribe((v) => {
            setProfileCookie(v);
            self.loadProfileInfo();
        });

        window.addEventListener("storage", (event) => {
            if (event.key !== selectedProfileKey) {
                return;
            }

            const latest = getProfileCookie() || "";
            if ((self.selectedProfile() || "") !== latest) {
                self.selectedProfile(latest);
            }
        });

        self.loadProfileInfo();
        if (self.selectedProfile()) {
            setProfileCookie(self.selectedProfile());
        }
    }
}
