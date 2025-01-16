module default {
    type Shortlink {
        required property shortname -> str {
            constraint exclusive;
        }
        required property url -> str;
    }
}
