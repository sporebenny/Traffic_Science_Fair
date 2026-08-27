// ==========================
// Traffic Science Fair
// Mission 14 - Step 7-1
// Leaflet 基礎地圖
// ==========================


const map = L.map("map", {
    minZoom: 9,
    maxZoom: 18,
    maxBoundsViscosity: 1.0
});


// OpenStreetMap 底圖
L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);





// ==========================
// Mission 14 - Step 7-1
// 桃園－雙北研究區域
// ==========================

const studyArea = [
    [24.85, 121.20],   // 西南
    [25.20, 121.70]    // 東北
];


// 設定初始視野
map.fitBounds(studyArea);


// 限制地圖可移動範圍
map.setMaxBounds(studyArea);
