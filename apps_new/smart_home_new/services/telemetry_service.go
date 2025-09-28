package services

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// TelemetryService работает с сервисом телеметрии
type TelemetryService struct {
	BaseURL    string
	HTTPClient *http.Client
}

type TelemetryResponse struct {
	SensorID  int       `json:"sensorId"`
	Value     float64   `json:"value"`
	Timestamp time.Time `json:"timestamp"`
}

func NewTelemetryService(baseURL string) *TelemetryService {
	return &TelemetryService{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (s *TelemetryService) GetTelemetryBySensorID(sensorID int) ([]TelemetryResponse, error) {
	url := fmt.Sprintf("%s/api/v1/telemetry/%d", s.BaseURL, sensorID)

	resp, err := s.HTTPClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("error fetching telemetry data: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	var telemetry []TelemetryResponse
	if err := json.NewDecoder(resp.Body).Decode(&telemetry); err != nil {
		return nil, fmt.Errorf("error decoding telemetry response: %w", err)
	}

	return telemetry, nil
}
