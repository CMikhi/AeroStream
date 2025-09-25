/* eslint-disable prettier/prettier */
import {
    CanActivate,
    ExecutionContext,
    Injectable,
    ForbiddenException,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { Reflector } from '@nestjs/core';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    const requiredRoles = this.reflector.get<string[]>('roles', context.getHandler());
    if (!requiredRoles) {
      return true;
    }
    
    const { user } = context.switchToHttp().getRequest();
    if (!user) { throw new ForbiddenException('User not authenticated'); }
    
    if (!user.roles || !Array.isArray(user.roles)) {
      throw new ForbiddenException('User roles not found');
    }
    
    const hasRole = requiredRoles.some(role => user.roles.includes(role));
    if (!hasRole) { throw new ForbiddenException('Insufficient permissions'); }

    return true;
  }
}