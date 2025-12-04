import {
  Injectable,
  Logger,
  OnModuleDestroy,
  OnModuleInit,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import Bonjour, { Service } from "bonjour-service";
import * as os from "os";

/**
 * Service for mDNS/DNS-SD advertisement of the Ignite server.
 * Allows clients to discover the server on the local network without
 * knowing its IP address.
 */
@Injectable()
export class DiscoveryService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(DiscoveryService.name);
  private bonjour: Bonjour | null = null;
  private publishedService: Service | null = null;

  // Service type follows DNS-SD naming conventions
  private readonly serviceType = "ignite-chat";
  private readonly serviceName: string;

  constructor(private readonly configService: ConfigService) {
    const hostname = os.hostname().replace(/\.local$/, "");
    this.serviceName = `IgniteServer-${hostname}`;
  }

  async onModuleInit(): Promise<void> {
    // Check if discovery is disabled via environment variable
    const disabled = this.configService.get<string>("DISABLE_MDNS") === "true";
    if (disabled) {
      this.logger.log("mDNS discovery disabled via DISABLE_MDNS environment variable");
      return;
    }

    await this.advertise();
  }

  async onModuleDestroy(): Promise<void> {
    await this.stop();
  }

  /**
   * Start advertising the server via mDNS/DNS-SD.
   */
  async advertise(): Promise<void> {
    if (this.bonjour) {
      this.logger.warn("mDNS service already advertising");
      return;
    }

    try {
      this.bonjour = new Bonjour();

      const port = parseInt(
        this.configService.get<string>("PORT") || "5200",
        10,
      );

      // Get server version from package.json or environment
      const version = this.configService.get<string>("SERVER_VERSION") || "1.0.0";

      this.publishedService = this.bonjour.publish({
        name: this.serviceName,
        type: this.serviceType,
        port: port,
        txt: {
          version: version,
          protocol: "http",
          websocket: "true",
          path: "/",
        },
      });

      this.logger.log(
        `mDNS: Advertising "${this.serviceName}" on port ${port} as _${this.serviceType}._tcp`,
      );
    } catch (error) {
      this.logger.error("Failed to start mDNS advertisement", error);
    }
  }

  /**
   * Stop advertising the server.
   */
  async stop(): Promise<void> {
    if (this.publishedService) {
      try {
        this.publishedService.stop?.();
        this.publishedService = null;
      } catch (error) {
        this.logger.warn("Error stopping mDNS service", error);
      }
    }

    if (this.bonjour) {
      try {
        this.bonjour.destroy();
        this.bonjour = null;
      } catch (error) {
        this.logger.warn("Error destroying Bonjour instance", error);
      }
    }

    this.logger.log("mDNS advertisement stopped");
  }

  /**
   * Get the current service name being advertised.
   */
  getServiceName(): string {
    return this.serviceName;
  }

  /**
   * Check if the service is currently being advertised.
   */
  isAdvertising(): boolean {
    return this.publishedService !== null;
  }
}
