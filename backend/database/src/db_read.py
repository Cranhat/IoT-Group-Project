def create_fetch():
    return """
            SELECT {0}
            FROM {1};
            """
    
def create_fetch_where():
    return """
            SELECT {0}
            FROM {1}
            WHERE {2};
            """