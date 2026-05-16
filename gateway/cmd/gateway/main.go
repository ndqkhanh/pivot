package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"go.opentelemetry.io/collector/pdata/ptrace/ptraceotlp"
	"google.golang.org/grpc"
)

const (
	defaultGRPCPort = "4317"
	defaultHTTPPort = "4318"
)

// Gateway is the main OTLP receiver and policy enforcement service
type Gateway struct {
	grpcServer *grpc.Server
	httpServer *http.Server
	config     *Config
}

// Config holds gateway configuration
type Config struct {
	GRPCPort         string
	HTTPPort         string
	ClickHouseURL    string
	PolicyEngineURL  string
	EnablePolicyEnforcement bool
}

// NewGateway creates a new gateway instance
func NewGateway(config *Config) *Gateway {
	return &Gateway{
		config: config,
	}
}

// Start starts the gateway services
func (g *Gateway) Start(ctx context.Context) error {
	// Start gRPC server
	go func() {
		if err := g.startGRPC(); err != nil {
			log.Printf("gRPC server error: %v", err)
		}
	}()

	// Start HTTP server
	go func() {
		if err := g.startHTTP(); err != nil {
			log.Printf("HTTP server error: %v", err)
		}
	}()

	log.Println("Gateway started successfully")
	log.Printf("gRPC listening on :%s", g.config.GRPCPort)
	log.Printf("HTTP listening on :%s", g.config.HTTPPort)

	return nil
}

// startGRPC starts the gRPC OTLP receiver
func (g *Gateway) startGRPC() error {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", g.config.GRPCPort))
	if err != nil {
		return fmt.Errorf("failed to listen: %v", err)
	}

	g.grpcServer = grpc.NewServer()

	// Register OTLP trace service
	traceService := &TraceService{gateway: g}
	ptraceotlp.RegisterGRPCServer(g.grpcServer, traceService)

	log.Printf("Starting gRPC server on :%s", g.config.GRPCPort)
	return g.grpcServer.Serve(lis)
}

// startHTTP starts the HTTP OTLP receiver
func (g *Gateway) startHTTP() error {
	// HTTP implementation
	return nil
}

// Stop gracefully stops the gateway
func (g *Gateway) Stop() {
	if g.grpcServer != nil {
		g.grpcServer.GracefulStop()
	}
	log.Println("Gateway stopped")
}

func main() {
	config := &Config{
		GRPCPort:         getEnv("PIVOT_GRPC_PORT", defaultGRPCPort),
		HTTPPort:         getEnv("PIVOT_HTTP_PORT", defaultHTTPPort),
		ClickHouseURL:    getEnv("CLICKHOUSE_URL", "http://localhost:8123"),
		PolicyEngineURL:  getEnv("POLICY_ENGINE_URL", "http://localhost:8181"),
		EnablePolicyEnforcement: getEnv("ENABLE_POLICY", "true") == "true",
	}

	gateway := NewGateway(config)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	if err := gateway.Start(ctx); err != nil {
		log.Fatalf("Failed to start gateway: %v", err)
	}

	// Wait for interrupt signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	<-sigChan

	log.Println("Shutting down gateway...")
	gateway.Stop()
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
