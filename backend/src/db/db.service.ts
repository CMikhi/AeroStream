/* eslint-disable prettier/prettier */
import {
	ConflictException,
	Injectable,
	UnauthorizedException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm/dist/common/typeorm.decorators';

import { Repository } from 'typeorm';

import { User } from '../entities/user.entity';
import { UpdateUserDto } from 'src/dto/update-user.dto';

@Injectable()
export class DbService {
	constructor(
		@InjectRepository(User)
		private readonly userRepository: Repository<User>,
		// private readonly authService: AuthService, // Cannot use AuthService
	) {}
	// TODO: Remove findAll() method, replace require parameters
	async findAll(): Promise<User[]> {
		return await this.userRepository.find();
	}

	async create(user: User): Promise<User | undefined> {
		// Check for existing user by username
		const existingUserByUsername = await this.findOne(undefined, user.username);
		
		if (existingUserByUsername) {
			throw new ConflictException('User already exists');
		}
		return await this.userRepository.save(user);
	}

	async findOne(uuid?: string, username?: string): Promise<User | null> {
		if (uuid) {
			return await this.userRepository.findOne({ where: { id: uuid } });
		}
		if (username) {
			return await this.userRepository.findOne({ where: { username } });
		}
		return null;
	}

	async remove(uuid: string): Promise<User | undefined> {
		const user = await this.userRepository.findOne({
			where: { id: uuid },
		});
		if (!user) {
			return undefined;
		}
		await this.userRepository.remove(user);
		return user;
	}

	async update(uuid: string, updateUserDto: UpdateUserDto): Promise<User | undefined> {
		const user = await this.userRepository.findOne({
			where: { id: uuid },
		});
		if (!user) {
			return undefined;
		}
		Object.assign(user, updateUserDto);
		return await this.userRepository.save(user);
	}

	async updateRole(uuid: string, role: string): Promise<User | undefined> {
		const user = await this.userRepository.findOne({
			where: { id: uuid },
		});
		if (!user) {
			throw new UnauthorizedException();
		}
		user.role = role;
		return await this.userRepository.save(user);
	}

	async SaveRefreshToken(userId: string, refreshTokenHash: string): Promise<void> {
		let user: User | null;
		if (!(user = await this.findOne(userId, undefined))) {
			throw new UnauthorizedException();
		}
		user.refreshTokenHash = refreshTokenHash;
		await this.userRepository.save(user);
	}
}

