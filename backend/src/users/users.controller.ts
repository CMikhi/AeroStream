/* eslint-disable prettier/prettier */
import { Controller, Get, Param, Body, Patch, Delete, UseGuards, Request } from '@nestjs/common';
import { DbService } from '../db/db.service';
import { UpdateUserDto } from '../dto/update-user.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from '../roles/roles.guard';
import { Roles } from '../roles/roles.decorator';
import { UserRole } from '../roles/roles.service';

interface AuthenticatedRequest {
	user: {
		id: string;
		email: string;
		username: string;
		role: string;
	}
}

@Controller('users')
@UseGuards(JwtAuthGuard) // All user endpoints require authentication
export class UsersController {
	constructor(private readonly usersService: DbService) {}

	@Get()
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN)
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
				username: user.username,
				createdAt: user.createdAt,
				role: user.role,
			})),
		};
	}

	@Get('me')
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN, UserRole.USER)
	async findOne(@Request() req: AuthenticatedRequest) {
		const user = await this.usersService.findOne(req.user.id);
		if (!user) {
			return { message: 'User not found', status: 404, data: undefined };
		}

		return {
			message: 'User retrieved successfully',
			status: 200,
			data: {
				id: user.id,
				username: user.username,
				createdAt: user.createdAt,
				role: user.role,
			},
		};
	}

	@Delete(':uuid')
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN) 
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
				username: user.username,
			},
		};
	}

	@Patch(':uuid')
	@UseGuards(RolesGuard)
	@Roles(UserRole.ADMIN, UserRole.USER)
	async updateUser(
		@Body() updateUserDto: UpdateUserDto, 
		@Request() req: AuthenticatedRequest
	) {
		const updatedUser = await this.usersService.update(req.user.id, updateUserDto);
		if (!updatedUser) {
			return { message: 'User not found', status: 404 };
		}
		return {
			message: 'User updated successfully',
			status: 200,
		};
	}
}
