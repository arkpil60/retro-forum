from datetime import datetime, timedelta

def convert_to_retro(real_timestamp: datetime) -> datetime:
    
    if not isinstance(real_timestamp, datetime):
        return real_timestamp
        
    retro_years_shift = timedelta(days=7305)
    return real_timestamp - retro_years_shift
