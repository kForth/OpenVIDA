function openLinkDoc(docId, isCallout, targetElement, sourceElement, isButton) {
    if (docId !== null && docId.length != 0) {
        window.location = `/document/${docId}`;
    } else if (sourceElement !== null && sourceElement.length != 0) {
        window.location = `/doclink/${sourceElement}`;
    }
}

function openImage(imageURL, imgId) {
    window.open(
        `${imageURL}?AsPage=true`,
        "image",
        "popup=true,width=400,height=400"
    );
}

function imgSize(image) {}
