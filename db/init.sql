CREATE TABLE IF NOT EXISTS pictures (
    id CHAR(36) PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    date DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    tag VARCHAR(32) NOT NULL,
    picture_id CHAR(36) NOT NULL,
    confidence FLOAT NOT NULL,
    date DATETIME NOT NULL,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
);
