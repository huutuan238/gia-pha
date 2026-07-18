from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return jsonify(
        [
    {
        "data": {
            "avatar": "",
            "birthday": 1930,
            "death_date": 2013,
            "full name": "Nguyen Huu Khuong",
            "gender": "M",
            "hometown": "My Thanh",
            "last name": "",
            "note": ""
        },
        "id": "12a9bddf-855a-4583-a695-c73fa8c0e9b2",
        "rels": {
            "children": [
                "0fa5c6bc-5b58-40f5-a07e-d787e26d8b56",
                "f12db64d-f028-4418-b0e1-8eda22ab386d"
            ],
            "spouses": [
                "bd56a527-b613-474d-9f38-fcac0aae218b"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Nguyen Thi Thien",
            "gender": "F"
        },
        "id": "bd56a527-b613-474d-9f38-fcac0aae218b",
        "rels": {
            "children": [
                "0fa5c6bc-5b58-40f5-a07e-d787e26d8b56",
                "f12db64d-f028-4418-b0e1-8eda22ab386d"
            ],
            "spouses": [
                "12a9bddf-855a-4583-a695-c73fa8c0e9b2"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Andrea",
            "gender": "F"
        },
        "id": "8c92765f-92d3-4120-90dd-85a28302504c",
        "rels": {
            "children": [
                "ce2fcb9a-6058-4326-b56a-aced35168561"
            ],
            "parents": [
                "d8897e67-db7c-4b72-ae7c-69aae266b140",
                "9397093b-30bb-420b-966f-62596b58447f"
            ],
            "spouses": [
                "0"
            ]
        }
    },
        {
        "data": {
            "avatar": "https://static8.depositphotos.com/1009634/988/v/950/depositphotos_9883921-stock-illustration-no-user-profile-picture.jpg",
            "birthday": "1998",
            "education": "Dai học",
            "full name": "Tuan",
            "gender": "M"
        },
        "id": "0",
        "rels": {
            "children": [
                "ce2fcb9a-6058-4326-b56a-aced35168561"
            ],
            "parents": [
                "0c09cfa0-5e7c-4073-8beb-94f6c69ada19",
                "0fa5c6bc-5b58-40f5-a07e-d787e26d8b56"
            ],
            "spouses": [
                "8c92765f-92d3-4120-90dd-85a28302504c"
            ]
        }
    },
    {
        "data": {
            "birthday": "",
            "education": "",
            "full name": "Huu Khuyen",
            "gender": "M",
            "hometown": ""
        },
        "id": "acebe83c-630e-4d34-8078-e4627f03f0b5",
        "rels": {
            "parents": [
                "12a9bddf-855a-4583-a695-c73fa8c0e9b2",
                "bd56a527-b613-474d-9f38-fcac0aae218b"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Nguyen Huu Vinh",
            "gender": "M"
        },
        "id": "0fa5c6bc-5b58-40f5-a07e-d787e26d8b56",
        "rels": {
            "children": [
                "0"
            ],
            "parents": [
                "12a9bddf-855a-4583-a695-c73fa8c0e9b2",
                "bd56a527-b613-474d-9f38-fcac0aae218b"
            ],
            "spouses": [
                "0c09cfa0-5e7c-4073-8beb-94f6c69ada19"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Nguyen Thi Yen",
            "gender": "F"
        },
        "id": "0c09cfa0-5e7c-4073-8beb-94f6c69ada19",
        "rels": {
            "children": [
                "0"
            ],
            "spouses": [
                "0fa5c6bc-5b58-40f5-a07e-d787e26d8b56"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Ben",
            "gender": "M"
        },
        "id": "ce2fcb9a-6058-4326-b56a-aced35168561",
        "rels": {
            "children": [
                "eabd40c9-4518-4485-af5e-e4bc3ffd27fb",
                "240a3f71-c921-42d7-8a13-dec5e1acc4fd"
            ],
            "parents": [
                "0",
                "8c92765f-92d3-4120-90dd-85a28302504c"
            ],
            "spouses": [
                "b4e33c68-20a7-47ba-9dcc-1168a07d5b52"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Carlos",
            "gender": "M"
        },
        "id": "eabd40c9-4518-4485-af5e-e4bc3ffd27fb",
        "rels": {
            "parents": [
                "ce2fcb9a-6058-4326-b56a-aced35168561",
                "b4e33c68-20a7-47ba-9dcc-1168a07d5b52"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Branka",
            "gender": "F"
        },
        "id": "b4e33c68-20a7-47ba-9dcc-1168a07d5b52",
        "rels": {
            "children": [
                "eabd40c9-4518-4485-af5e-e4bc3ffd27fb",
                "240a3f71-c921-42d7-8a13-dec5e1acc4fd"
            ],
            "spouses": [
                "ce2fcb9a-6058-4326-b56a-aced35168561"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Carla",
            "gender": "F"
        },
        "id": "240a3f71-c921-42d7-8a13-dec5e1acc4fd",
        "rels": {
            "parents": [
                "ce2fcb9a-6058-4326-b56a-aced35168561",
                "b4e33c68-20a7-47ba-9dcc-1168a07d5b52"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Zadro",
            "gender": "M"
        },
        "id": "d8897e67-db7c-4b72-ae7c-69aae266b140",
        "rels": {
            "children": [
                "8c92765f-92d3-4120-90dd-85a28302504c"
            ],
            "spouses": [
                "9397093b-30bb-420b-966f-62596b58447f"
            ]
        }
    },
    {
        "data": {
            "avatar": "",
            "birthday": "",
            "full name": "Zadra",
            "gender": "F"
        },
        "id": "9397093b-30bb-420b-966f-62596b58447f",
        "rels": {
            "children": [
                "8c92765f-92d3-4120-90dd-85a28302504c"
            ],
            "spouses": [
                "d8897e67-db7c-4b72-ae7c-69aae266b140"
            ]
        }
    },
    {
        "id": "f12db64d-f028-4418-b0e1-8eda22ab386d",
        "data": {
            "gender": "M",
            "full name": "Huu Khuyen",
            "birthday": "",
            "hometown": "",
            "education": ""
        },
        "rels": {
            "parents": [
                "12a9bddf-855a-4583-a695-c73fa8c0e9b2",
                "bd56a527-b613-474d-9f38-fcac0aae218b"
            ],
            "spouses": [
                "4cf4163e-3da9-4304-9209-05030966497e"
            ]
        }
    },
    {
        "id": "4cf4163e-3da9-4304-9209-05030966497e",
        "data": {
            "gender": "F",
            "full name": "Nguyen Thi Minh",
            "birthday": "",
            "hometown": "",
            "education": ""
        },
        "rels": {
            "spouses": [
                "f12db64d-f028-4418-b0e1-8eda22ab386d"
            ]
        }
    }
]
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)