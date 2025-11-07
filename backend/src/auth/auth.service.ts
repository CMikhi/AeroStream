/* eslint-disable prettier/prettier */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-call */
import {
	BadRequestException,
	Injectable,
	UnauthorizedException,
} from '@nestjs/common';
import bcrypt from 'bcrypt';

import { DbService } from '../db/db.service'; // Should prob move into own db file later
import { JwtService } from '../jwt/jwt.service';

import { CreateUserDto } from 'src/dto/CreateUser.dto';
import { loginUserDto } from 'src/dto/loginUser.dto';
import { User } from 'src/entities/user.entity';

@Injectable()
export class AuthService {
	constructor(
		private readonly dbService: DbService,
		private readonly jwtService: JwtService,
	) {}

	/**
	 * Authenticates a user by validating their username and password credentials.
	 * If parameters are invalid, placeholder hashes and IDs are used to prevent timing 
	 * attacks, but are still rejected, even if placeholder hash is correct.
	 *
	 * @param loginUserDto - Login credentials containing username and password
	 * @returns A promise that resolves to an object containing a success message and authentication token
	 * @throws {Error} When username or password are missing
	 * @throws {Error} When user with the provided username is not found
	 * @throws {Error} When the provided password doesn't match the stored hash
	 *
	 * @example
	 * ```typescript
	 * const result = await authService.login({ username: 'cam', password: '123456' });
	 * console.log(result.message); // "User logged in successfully"
	 * console.log(result.accessToken);   // JWT access token
	 * ```
	 */
	async login(loginUserDto: loginUserDto): Promise<{ message: string; userID: string; accessToken: string; refreshToken: string; }> {
		// Find user by username
		const user: User | null = await this.dbService.findOne(undefined, loginUserDto.username);

		let isValid = !!user; // Assume invalid unless proven otherwise
		const passwordHash = user?.password ?? '$2b$10$C6UzMDM.H6dfI/f/IKcEeO1jJXclB/6L6iRHIx6e.C5F9jq5Hn4e.';

		if (!await bcrypt.compare(loginUserDto.password, passwordHash)) {
			isValid = false;
		}

		const userId = user?.id ?? 'ycuvybuuyvyderyfutg7iyunhbgjftru';
		const userRole = user?.role ?? "USER";

		const tokens = await this.jwtService.rotateTokens(userId, userRole);

		// Wait until end to return Error to prevent Timing Attacks
		if (!isValid) {
			throw new UnauthorizedException('Invalid credentials');
		}

		await this.dbService.SaveRefreshToken(userId, tokens.refreshTokenHash);
		return {
			message: 'User logged in successfully',
			userID: userId,
			accessToken: tokens.accessToken,
			refreshToken: tokens.refreshToken,
		};
	}

	/**
	 * Registers a new user with the provided username and password.
	 *
	 * @param createUserDto - The user's registration data containing username and password
	 * @returns A promise that resolves to an object containing a success message and the user's ID
	 * @throws {Error} When username or password is missing
	 * @throws {Error} When password hashing fails
	 *
	 * @example
	 * ```typescript
	 * const result = await authService.register({ username: 'newuser', password: 'securePassword123' });
	 * console.log(result); // { message: 'User registered successfully', userID: 'uuid' }
	 * ```
	 */
	async register(createUserDto: CreateUserDto): Promise<{ message: string; userID: string; accessToken: string; refreshToken: string; }> {
		const saltRounds = 12;

		// Check if user already exists
		if (await this.dbService.findOne(undefined, createUserDto.username)) {
			throw new BadRequestException('User already exists');
		}

		// Hash the password
		let hashedPassword: string;
		try {
			hashedPassword = await bcrypt.hash(
				createUserDto.password,
				saltRounds,
			) as string;
		} catch {
			throw new Error('Error hashing password');
		}

		// Store user with encrypted password (Login compares password to hash)
		let user: User = {
			...createUserDto,
			password: hashedPassword,
			createdAt: new Date(),
			id: undefined,
			role: createUserDto.role || 'user',
			refreshTokenHash: '',
		};

		user = (await this.dbService.create(user)) as User;

		if (!user || !user.id) throw new Error('Error creating user');

		const { accessToken, refreshToken, refreshTokenHash } = await this.jwtService.rotateTokens(user.id, user.role);

		await this.dbService.SaveRefreshToken(user.id, refreshTokenHash);

		return {
			message: 'User registered successfully',
			userID: user.id,
			accessToken,
			refreshToken,
		};
	}

	/**
	 * Refreshes the authentication token for the logged-in user.
	 *
	 * @param refreshToken - The refresh token to validate and use for generating new tokens
	 * @returns A promise that resolves to an object containing a success message and the user's new tokens
	 * @throws {UnauthorizedException} When refresh token is invalid or expired
	 * @throws {UnauthorizedException} When user is not found or has no stored refresh token
	 *
	 * @example
	 * ```typescript
	 * const result = await authService.refresh('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');
	 * console.log(result.accessToken); // New access token
	 * console.log(result.newRefreshToken); // New refresh token
	 * ```
	 */
	async refresh(refreshToken: string): Promise<{ message: string; accessToken: string; newRefreshToken: string; }> {
		// Decode the refresh token to extract user ID
		const payload = this.jwtService.decodeToken(refreshToken);
		if (!payload || !payload.sub) {
			throw new UnauthorizedException('Invalid refresh token');
		}

		const userId: string = payload.sub;
		const user = await this.dbService.findOne(userId);
		if (!user?.id || !user.refreshTokenHash) {
			throw new UnauthorizedException('User not found or refresh token not set');
		}

		const isValid = await this.jwtService.compareToken(
			refreshToken,
			user.refreshTokenHash,
		);

		if (!isValid) {
			throw new UnauthorizedException('Invalid refresh token');
		}

		const { accessToken, refreshToken: newRefreshToken, refreshTokenHash } = await this.jwtService.rotateTokens(user.id, user.role);

		await this.dbService.SaveRefreshToken(user.id, refreshTokenHash);

		return {
			message: 'Token refreshed successfully',
			accessToken,
			newRefreshToken,
		};
	}

	async getLoggedIn(accessToken: string): Promise<{ loggedIn: boolean; userId?: string }> {
		try {
			return { loggedIn: await this.jwtService.verifyToken(accessToken) };
		} catch (error) {
			// Suppress noisy log output during tests but keep for other environments
			console.log('Error verifying token', error as Error);
			return { loggedIn: false };
		}
	}
}
