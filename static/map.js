// ==========================
// Traffic Science Fair
// Mission 14 - Step 7-2
// Leaflet + Flask Route API
// ==========================


const map = L.map("map", {
    minZoom: 9,
    maxZoom: 18,
    maxBoundsViscosity: 1.0
});


// ==========================
// OpenStreetMap
// ==========================

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// ==========================
// 桃園－雙北研究區域
// ==========================

const studyArea = [
    [24.85, 121.20],
    [25.20, 121.70]
];


// 初始視野
map.fitBounds(studyArea);


// 限制地圖拖曳範圍
map.setMaxBounds(studyArea);





// ==========================
// Case Selector
// ==========================

const caseSelector =
    document.getElementById("caseSelector");


let selectedCase =
    caseSelector.value;


// ==========================
// Route Layer
// ==========================

let routeLayer = null;


// ==========================
// Endpoint Marker
// ==========================

let startMarker = null;
let endMarker = null;


// ==========================
// Case Information
// ==========================

const caseInfo = {

    "1": {
        endName: "台北車站",
        endLat: 25.0478,
        endLon: 121.5170
    },

    "2": {
        endName: "西門町",
        endLat: 25.0420,
        endLon: 121.5081
    },

    "3": {
        endName: "信義計畫區（台北101）",
        endLat: 25.0330,
        endLon: 121.5654
    }
};


// ==========================
// Load Routes
// ==========================

function loadRoutes(caseNumber) {

    fetch(`/api/routes?case=${caseNumber}`)

        .then(response => {

            if (!response.ok) {

                throw new Error(
                    `API request failed: ${response.status}`
                );

            }

            return response.json();

        })

        .then(data => {

            console.log(
                "Route API data:",
                data
            );


            // ==========================
            // 移除舊 Route
            // ==========================

            if (routeLayer !== null) {

                map.removeLayer(routeLayer);

            }


            // ==========================
            // 建立新 Route
            // ==========================


            // ==========================
            // Case 3 Route 延伸至研究終點
            // ==========================

            let displayRoute1 = data.route1;
            let displayRoute2 = data.route2;
            let displayRoute3 = data.route3;

            if (caseNumber === "3") {

                displayRoute1 = [
                    ...data.route1,
                    [25.0330, 121.5654]
                ];

                displayRoute2 = [
                    ...data.route2,
                    [25.0330, 121.5654]
                ];

                displayRoute3 = [
                    ...data.route3,
                    [25.0330, 121.5654]
                ];
            }


            

            const route1 = L.polyline(
                displayRoute1,
                {
                    color: "blue",
                    weight: 6,
                    opacity: 0.7
                }
            );


            const route2 = L.polyline(
                displayRoute2,
                {
                    color: "red",
                    weight: 4,
                    opacity: 0.7
                }
            );


            const route3 = L.polyline(
                displayRoute3,
                {
                    color: "green",
                    weight: 2,
                    opacity: 0.7
                }
            );


            routeLayer = L.layerGroup([

                route1,
                route2,
                route3

            ]);


            routeLayer.addTo(map);


            // ==========================
            // 起點 Marker
            // ==========================

            if (startMarker !== null) {

                map.removeLayer(
                    startMarker
                );

            }


            startMarker = L.marker([
                24.9896,
                121.3136
            ])
            .addTo(map)
            .bindPopup(
                "<b>桃園車站</b>"
            );


            // ==========================
            // 終點 Marker
            // ==========================

            if (endMarker !== null) {

                map.removeLayer(
                    endMarker
                );

            }


            const info =
                caseInfo[caseNumber];


            endMarker = L.marker([
                info.endLat,
                info.endLon
            ])
            .addTo(map)
            .bindPopup(
                `<b>${info.endName}</b>`
            );


            // ==========================
            // 自動調整地圖視野
            // ==========================

            const allFeatures =
                L.featureGroup([

                    route1,
                    route2,
                    route3,
                    startMarker,
                    endMarker

                ]);


            map.fitBounds(
                allFeatures.getBounds(),
                {
                    padding: [30, 30]
                }
            );

        })

        .catch(error => {

            console.error(
                "Route API error:",
                error
            );

        });

}


// ==========================
// Case 切換事件
// ==========================

caseSelector.addEventListener(
    "change",
    function () {

        selectedCase =
            this.value;

        loadRoutes(
            selectedCase
        );

    }
);


// ==========================
// 初始載入
// ==========================

loadRoutes(
    selectedCase
);






fetch(`/api/routes?case=${selectedCase}`)
    .then(response => {

        if (!response.ok) {
            throw new Error(
                `API request failed: ${response.status}`
            );
        }

        return response.json();
    })

    .then(data => {

        console.log("Route API data:", data);


        // ==========================
        // Route 1：最短距離
        // ==========================

        const route1 = L.polyline(
            data.route1,
            {
                color: "blue",
                weight: 6,
                opacity: 0.7
            }
        ).addTo(map);


        // ==========================
        // Route 2：最短時間
        // ==========================

        const route2 = L.polyline(
            data.route2,
            {
                color: "red",
                weight: 4,
                opacity: 0.7
            }
        ).addTo(map);


        // ==========================
        // Route 3：折衷 Route
        // ==========================

        const route3 = L.polyline(
            data.route3,
            {
                color: "green",
                weight: 2,
                opacity: 0.7
            }
        ).addTo(map);


        // ==========================
        // 起點
        // ==========================

        L.marker([
            24.9896,
            121.3136
        ])
        .addTo(map)
        .bindPopup(
            "<b>桃園車站</b>"
        );


        // ==========================
        // 終點
        // ==========================

        let endLat = 25.0478;
        let endLon = 121.5170;
        let endName = "台北車站";

        if (selectedCase === "2") {

            endLat = 25.0420;
            endLon = 121.5081;
            endName = "西門町";

        }

        else if (selectedCase === "3") {

            endLat = 25.0330;
            endLon = 121.5654;
            endName = "信義計畫區";

        }


        L.marker([
            endLat,
            endLon
        ])
        .addTo(map)
        .bindPopup(
            `<b>${endName}</b>`
        );

        // ==========================
        // 自動調整視野
        // ==========================

        const routeGroup = L.featureGroup([
            route1,
            route2,
            route3
        ]);

        map.fitBounds(
            routeGroup.getBounds(),
            {
                padding: [30, 30]
            }
        );

    })

    .catch(error => {

        console.error(
            "Route API error:",
            error
        );

    });




    