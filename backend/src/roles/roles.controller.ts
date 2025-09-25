/* eslint-disable prettier/prettier */
import {
  Body,
  Controller,
  Get,
  Param,
  Patch,
  UseGuards,
} from "@nestjs/common";
import { RolesService, UserRole } from "./roles.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { RolesGuard } from "./roles.guard";
import { Roles } from "./roles.decorator";

@Controller("roles")
@UseGuards(JwtAuthGuard) // Require authentication for all role endpoints
export class RolesController {
  constructor(private readonly rolesService: RolesService) {}

  @Get(":uuid")
  @UseGuards(RolesGuard)
  @Roles(UserRole.ADMIN) // Only admins can view roles
  async getRole(@Param("uuid") uuid: string) {
    const role = await this.rolesService.getRole(uuid);
    if (!role) {
      return { message: "User not found", status: 404, data: undefined };
    }
    return {
      message: "Role retrieved successfully",
      status: 200,
      data: role,
    };
  }
  
  @Patch(":uuid")
  @UseGuards(RolesGuard)
  @Roles(UserRole.ADMIN) // Only admins can update roles
  async updateUser(
      @Param("uuid") uuid: string,
      @Body("role") role: string,
  ) {
      // Validate role before updating
      if (!this.rolesService.isValidRole(role)) {
          return { 
              message: "Invalid role. Valid roles are: " + Object.values(UserRole).join(", "), 
              status: 400 
          };
      }

      const updatedUser = await this.rolesService.update(uuid, role);
      if (!updatedUser) {
          return { message: "User not found", status: 404 };
      }
      return {
          message: "User role updated successfully",
          status: 200,
          data: { id: updatedUser.id, username: updatedUser.username, role: updatedUser.role },
      };
  }
}

