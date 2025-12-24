def get_paginator_range(paginator_length: int, current_page: int, total_pages: int):
    half_paginator = paginator_length // 2
    start = max(1, current_page - half_paginator)
    end = min(total_pages, max(current_page + half_paginator, paginator_length))
    return range(start, end + 1)