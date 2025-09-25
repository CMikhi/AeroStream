/* eslint-disable prettier/prettier */
import { Controller, Get, Param, Body, Patch, Delete, UseGuards } from '@nestjs/common';
import { DbService } from '../db/db.service';
import { UpdateUserDto } from '../dto/update-user.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from '../roles/roles.guard';
import { Roles } from '../roles/roles.decorator';
import { UserRole } from '../roles/roles.service';

@Controller('users')
@UseGuards(JwtAuthGuard) // All user endpoints require authentication
export class UsersController {
	constructor(private readonly usersService: DbService) {}

	@Get()
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN) // Only admins can list all users
	async findAll() {
		const users = await this.usersService.findAll();
		if (!users.length) {
			return { message: 'No users found', status: 404 };
		}
		return {
			message: 'Users retrieved successfully',
			status: 200,
			data: users.map((user) => ({
				id: user.id,
				email: user.email,
				firstName: user.firstName,
				lastName: user.lastName,
				createdAt: user.createdAt,
				role: user.role,
			})),
		};
	}

	@Get(':uuid')
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN, UserRole.USER) // Both admins and users can view user details
	async findOne(@Param('uuid') uuid: string) {
		const user = await this.usersService.findOne(uuid, undefined);
		if (!user) {
			return { message: 'User not found', status: 404, data: undefined };
		}
		// Don't return sensitive info like password hash and refresh token
		return {
			message: 'User retrieved successfully',
			status: 200,
			data: {
				id: user.id,
				email: user.email,
				firstName: user.firstName,
				lastName: user.lastName,
				createdAt: user.createdAt,
				role: user.role,
			},
		};
	}

	@Delete(':uuid')
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN) // Only admins can delete users
	async deleteUser(@Param('uuid') uuid: string) {
		const user = await this.usersService.remove(uuid);
		if (!user) {
			return { message: 'User not found', status: 404, data: undefined };
		}
		return {
			message: 'User deleted successfully',
			status: 200,
			data: {
				id: user.id,
				email: user.email,
				firstName: user.firstName,
				lastName: user.lastName,
			},
		};
	}

	@Patch(':uuid')
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN, UserRole.USER) // Both admins and users can update user info
	async updateUser(
		@Param('uuid') uuid: string,
		@Body() updateUserDto: UpdateUserDto,
	) {
		const updatedUser = await this.usersService.update(uuid, updateUserDto);
		if (!updatedUser) {
			return { message: 'User not found', status: 404 };
		}
		return {
			message: 'User updated successfully',
			status: 200,
			data: {
				id: updatedUser.id,
				email: updatedUser.email,
				firstName: updatedUser.firstName,
				lastName: updatedUser.lastName,
				role: updatedUser.role,
			},
		};
	}
}
