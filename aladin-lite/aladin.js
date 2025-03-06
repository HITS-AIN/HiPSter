var aladin;
A.init.then(() => {
    aladin = A.aladin('#aladin-lite-div', {fov:1, target: 'M81'});
});
