﻿namespace Bit.Splunk.Models
{
    public class EventsApiKey
    {
        public EventsApiKey()
        { }

        public EventsApiKey(string apiKey)
        {
            var parts = apiKey?.Split('_');
            if (parts != null && parts.Length > 1)
            {
                ClientId = parts[0];
                ClientSecret = parts[1];
            }
        }

        public string ClientId { get; set; }
        public string ClientSecret { get; set; }

        public override string ToString()
        {
            return $"{ClientId}_{ClientSecret}";
        }
    }
}
