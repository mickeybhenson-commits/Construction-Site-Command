import requests
import pandas as pd
from datetime import datetime, timedelta

class WeatherAPI:
    """
    Free weather forecast using Open-Meteo API
    No API key required, unlimited calls
    Documentation: https://open-meteo.com/
    """
    
    def __init__(self, latitude=35.726, longitude=-77.916):
        """
        Initialize for Wilson, NC (J&J site)
        
        Args:
            latitude: Site latitude (default: Wilson, NC)
            longitude: Site longitude (default: Wilson, NC)
        """
        self.lat = latitude
        self.lon = longitude
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_7day_forecast(self):
        """
        Get 7-day precipitation forecast with probability
        
        Returns:
            DataFrame with columns: date, precip_forecast, precip_prob, description
        """
        try:
            # API parameters for 7-day forecast
            params = {
                'latitude': self.lat,
                'longitude': self.lon,
                'daily': 'precipitation_sum,precipitation_probability_max,weathercode',
                'temperature_unit': 'fahrenheit',
                'precipitation_unit': 'inch',
                'timezone': 'America/New_York',
                'forecast_days': 7
            }
            
            # Make API call
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract daily data
            daily = data['daily']
            
            # Build forecast dataframe
            forecast_data = []
            for i in range(len(daily['time'])):
                date = daily['time'][i]
                precip = daily['precipitation_sum'][i] or 0.0
                precip_prob = daily['precipitation_probability_max'][i] or 0
                weather_code = daily['weathercode'][i]
                
                forecast_data.append({
                    'date': date,
                    'precip_forecast': round(precip, 2),
                    'precip_prob': precip_prob,
                    'description': self._weather_description(weather_code)
                })
            
            return pd.DataFrame(forecast_data)
            
        except Exception as e:
            print(f"Error fetching Open-Meteo forecast: {e}")
            return self._mock_forecast()
    
    def get_hourly_forecast(self, hours=24):
        """
        Get hourly precipitation forecast
        
        Args:
            hours: Number of hours to forecast (max 168)
        
        Returns:
            DataFrame with hourly precipitation data
        """
        try:
            params = {
                'latitude': self.lat,
                'longitude': self.lon,
                'hourly': 'precipitation,precipitation_probability,weathercode',
                'temperature_unit': 'fahrenheit',
                'precipitation_unit': 'inch',
                'timezone': 'America/New_York',
                'forecast_hours': min(hours, 168)
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            hourly = data['hourly']
            
            hourly_data = []
            for i in range(len(hourly['time'])):
                hourly_data.append({
                    'datetime': hourly['time'][i],
                    'precip': hourly['precipitation'][i] or 0.0,
                    'precip_prob': hourly['precipitation_probability'][i] or 0,
                    'condition': self._weather_description(hourly['weathercode'][i])
                })
            
            return pd.DataFrame(hourly_data)
            
        except Exception as e:
            print(f"Error fetching hourly forecast: {e}")
            return pd.DataFrame()
    
    def _weather_description(self, code):
        """
        Convert WMO weather code to description
        https://open-meteo.com/en/docs
        """
        weather_codes = {
            0: 'Clear',
            1: 'Mainly Clear',
            2: 'Partly Cloudy',
            3: 'Overcast',
            45: 'Foggy',
            48: 'Depositing Rime Fog',
            51: 'Light Drizzle',
            53: 'Moderate Drizzle',
            55: 'Dense Drizzle',
            61: 'Slight Rain',
            63: 'Moderate Rain',
            65: 'Heavy Rain',
            71: 'Slight Snow',
            73: 'Moderate Snow',
            75: 'Heavy Snow',
            77: 'Snow Grains',
            80: 'Slight Rain Showers',
            81: 'Moderate Rain Showers',
            82: 'Violent Rain Showers',
            85: 'Slight Snow Showers',
            86: 'Heavy Snow Showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with Slight Hail',
            99: 'Thunderstorm with Heavy Hail'
        }
        return weather_codes.get(code, 'Unknown')
    
    def _mock_forecast(self):
        """Fallback mock data if API fails"""
        today = datetime.now()
        forecast_dates = [(today + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(7)]
        
        return pd.DataFrame({
            'date': forecast_dates,
            'precip_forecast': [0.10, 0.25, 0.00, 0.15, 0.30, 0.05, 0.00],
            'precip_prob': [40, 60, 10, 50, 70, 30, 10],
            'description': ['Partly Cloudy', 'Moderate Rain', 'Clear', 'Slight Rain', 
                          'Heavy Rain', 'Light Drizzle', 'Clear']
        })
    
    def get_current_conditions(self):
        """Get current weather conditions"""
        try:
            params = {
                'latitude': self.lat,
                'longitude': self.lon,
                'current': 'temperature_2m,precipitation,weathercode,windspeed_10m,winddirection_10m',
                'temperature_unit': 'fahrenheit',
                'windspeed_unit': 'mph',
                'precipitation_unit': 'inch',
                'timezone': 'America/New_York'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['current']
            
            return {
                'temperature': current['temperature_2m'],
                'precipitation': current['precipitation'],
                'wind_speed': current['windspeed_10m'],
                'wind_direction': current['winddirection_10m'],
                'condition': self._weather_description(current['weathercode']),
                'time': current['time']
            }
            
        except Exception as e:
            print(f"Error fetching current conditions: {e}")
            return None

# Test the API
if __name__ == "__main__":
    print("Testing Open-Meteo API for Wilson, NC...\n")
    
    api = WeatherAPI()
    
    # Test 7-day forecast
    print("7-Day Forecast:")
    forecast = api.get_7day_forecast()
    print(forecast)
    print(f"\nTotal Forecast Precipitation: {forecast['precip_forecast'].sum():.2f} inches")
    
    # Test current conditions
    print("\n" + "="*50)
    print("Current Conditions:")
    current = api.get_current_conditions()
    if current:
        print(f"Temperature: {current['temperature']}°F")
        print(f"Wind: {current['wind_speed']} mph")
        print(f"Condition: {current['condition']}")
