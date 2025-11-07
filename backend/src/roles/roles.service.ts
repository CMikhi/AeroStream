/* eslint-disable prettier/prettier */
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { DbService } from '../db/db.service';
import { User } from '../entities/user.entity';

// enum to define user roles.
export enum UserRole {
    ADMIN = 'admin',
    USER = 'user',
}

@Injectable()
export class RolesService {
    constructor(private readonly dbService: DbService) {}
    private readonly roleHierarchy = {
        [UserRole.ADMIN]: [UserRole.ADMIN, UserRole.USER],
        [UserRole.USER]: [UserRole.USER],
    };

    hasPermission(userRoles: string[], requiredRoles: string[]): boolean {
    return requiredRoles.some(requiredRole => 
        userRoles.some(userRole => 
            this.roleHierarchy[userRole as UserRole]?.includes(requiredRole as UserRole)
        ));
    }
    
    getAllowedRoles(userRole: string): string[] {
        return this.roleHierarchy[userRole as UserRole] || [];
    }
    
    isValidRole(role: string): boolean {
        return Object.values(UserRole).includes(role as UserRole);
    }

	async getRole(userId: string): Promise<string> {
		let user: User | null;
		if (!(user = await this.dbService.findOne(userId, undefined))) {
			throw new UnauthorizedException();
		}
		return user.role;
	}

    async update(uuid: string, role: string): Promise<User | undefined> {
        const user = await this.dbService.updateRole(uuid, role);
        return user;
    }

    
}
