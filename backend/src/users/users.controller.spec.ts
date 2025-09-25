/* eslint-disable prettier/prettier */
import { Test, TestingModule } from '@nestjs/testing';
import { UsersController } from './users.controller';
import { DbService } from '../db/db.service';
import { AuthService } from '../auth/auth.service';
import { JwtService } from '../jwt/jwt.service';
import { RolesService } from '../roles/roles.service';

describe('UsersController', () => {
  let controller: UsersController;
  let db: any;

  beforeEach(async () => {
    db = {
      findAll: jest.fn(),
      findOne: jest.fn(),
      remove: jest.fn(),
      update: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [
        { provide: DbService, useValue: db },
        { provide: AuthService, useValue: {} },
        { provide: JwtService, useValue: {} },
        { provide: RolesService, useValue: {} },
      ],
    }).compile();

    controller = module.get<UsersController>(UsersController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('findAll', () => {
    it('returns 404 when no users', async () => {
      db.findAll.mockResolvedValue([]);
      const res = await controller.findAll();
      expect(res.status).toBe(404);
    });
    it('returns mapped users when present', async () => {
      db.findAll.mockResolvedValue([
        { id: '1', username: 'testuser', createdAt: new Date(), role: 'user' },
      ]);
      const res = await controller.findAll();
      expect(res.status).toBe(200);
      expect(res.data[0].username).toBe('testuser');
      expect(res.data[0].id).toBeDefined();
    });
  });

  describe('findOne', () => {
    it('returns 404 when user missing', async () => {
      db.findOne.mockResolvedValue(undefined);
      const res = await controller.findOne('x');
      expect(res.status).toBe(404);
    });
    it('returns sanitized user', async () => {
      db.findOne.mockResolvedValue({ id: '1', username: 'testuser', createdAt: new Date(), role: 'user', password: 'secret', refreshTokenHash: 'hash' });
      const res = await controller.findOne('1');
      expect(res.status).toBe(200);
      expect(res.data.password).toBeUndefined();
      expect(res.data.refreshTokenHash).toBeUndefined();
    });
  });

  describe('deleteUser', () => {
    it('returns 404 when not found', async () => {
      db.remove.mockResolvedValue(undefined);
      const res = await controller.deleteUser('x');
      expect(res.status).toBe(404);
    });
    it('returns deleted user meta', async () => {
      db.remove.mockResolvedValue({ id: '1', username: 'testuser' });
      const res = await controller.deleteUser('1');
      expect(res.status).toBe(200);
    });
  });

  describe('updateUser', () => {
    it('returns 404 when not found', async () => {
      db.update.mockResolvedValue(undefined);
      const res = await controller.updateUser('x', {} as any);
      expect(res.status).toBe(404);
    });
    it('returns updated user', async () => {
      db.update.mockResolvedValue({ id: '1', username: 'testuser', role: 'user' });
      const res = await controller.updateUser('1', { password: 'newpassword123!' } as any);
      expect(res.status).toBe(200);
      expect(res.data.username).toBe('testuser');
    });
  });
});