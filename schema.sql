DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS posts;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    original_picture BLOB NOT NULL,
    layer_composite BLOB NOT NULL,
    layer_clear BLOB NOT NULL,
    layer_salinity BLOB NOT NULL,
    layer_corrosion BLOB NOT NULL,
    layer_pitting BLOB NOT NULL,
    layer_oil BLOB NOT NULL,
    layer_recess BLOB NOT NULL,
    layer_ext_recess BLOB NOT NULL,
    clear_percentage INTEGER NOT NULL,
    salinity_percentage INTEGER NOT NULL,
    corrosion_percentage INTEGER NOT NULL,
    pitting_percentage INTEGER NOT NULL,
    oil_percentage INTEGER NOT NULL,
    recess_percentage INTEGER NOT NULL,
    ext_recess_percentage INTEGER NOT NULL,
    edit_salinity BLOB,
    edit_corrosion BLOB,
    edit_pitting BLOB,
    edit_oil BLOB,
    edit_recess BLOB,
    edit_ext_recess BLOB,
    FOREIGN KEY (author_id) REFERENCES user (id)
);