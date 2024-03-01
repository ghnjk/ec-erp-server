#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: mysql_backend
@author: jkguo
@create: 2024/2/24
"""
import logging
import typing
from datetime import datetime

import sqlalchemy
from sqlalchemy import create_engine, String, JSON, Integer, DateTime, sql, Column, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text
import json
from ec_erp_api.common import codec_util

func_declarative_base = declarative_base
DtoBase = sqlalchemy.orm.declarative_base()


class DtoUtil(object):

    @classmethod
    def to_dict(cls, o: object) -> dict:
        doc = {}
        for c in o.columns:
            try:
                v = o.__getattribute__(c)
                if isinstance(v, datetime):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
                doc[c] = v
            except Exception as ignoredE:
                pass
        return doc

    @classmethod
    def from_dict(cls, o: object, doc: dict):
        for c in o.columns:
            o.__setattr__(c, doc.get(c))

    @classmethod
    def copy(cls, src: object, dst: object):
        DtoUtil.from_dict(dst, DtoUtil.to_dict(src))


class ProjectDto(DtoBase):
    """
    项目表
    """
    __tablename__ = "t_project_info"
    __table_args__ = {"mysql_default_charset": "utf8"}
    project_id: Mapped[str] = Column('Fproject_id', String(128), primary_key=True, comment='项目ID')
    doc: Mapped[dict] = Column('Fdoc', JSON, comment='项目配置，对应ProjectConfig类')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0",
                                    comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0",
                                  comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="",
                                      comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='创建时间')
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='修改时间')


class UserDto(DtoBase):
    """
    用户信息表
    """
    __tablename__ = "t_user_info"
    __table_args__ = {"mysql_default_charset": "utf8"}
    user_name: Mapped[str] = Column('Fuser_name', String(128), primary_key=True, comment='用户名')
    default_project_id: Mapped[str] = Column('Fdefault_project_id', String(128), comment='默认项目')
    password: Mapped[str] = Column('Fpassword', String(256), comment='用户密码')
    roles: Mapped[list] = Column('Froles', JSON, comment='用户角色列表')
    is_admin: Mapped[int] = Column('Fis_admin', Integer, default=0, server_default="0",
                                   comment='是否管理员, 1: 管理员')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0",
                                    comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0",
                                  comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="",
                                      comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='创建时间')
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='修改时间')
    columns = [
        "user_name", "default_project_id", "password", "roles",
        "is_admin", "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]


class SupplierDto(DtoBase):
    """
    供应商信息
    """
    __tablename__ = "t_supplier_info"
    __table_args__ = ({
        "mysql_default_charset": "utf8"
    })
    supplier_id: Mapped[int] = Column('Fsupplier_id', Integer, primary_key=True, autoincrement=True, comment="供应商ID")
    project_id: Mapped[str] = Column('Fproject_id', String(128), index=True, comment='所属项目ID')
    supplier_name: Mapped[str] = Column('Fsupplier_name', String(128), index=True, comment='供应商名')
    wechat_account: Mapped[str] = Column('Fwechat_account', String(128), comment='供应商微信号')
    detail: Mapped[str] = Column('Fdetail', String(1024), comment='详细信息')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0",
                                    comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0",
                                  comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="",
                                      comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='创建时间')
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='修改时间')
    columns = [
        "supplier_id", "project_id", "supplier_name", "wechat_account",
        "detail", "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]


class SkuDto(DtoBase):
    """
    商品SKU信息
    """
    __tablename__ = "t_sku_info"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Fsku"
    ), {
                          "mysql_default_charset": "utf8"
                      })
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    sku: Mapped[str] = Column('Fsku', String(256), comment='商品SKU')
    sku_group: Mapped[str] = Column('Fsku_group', String(256), index=True, comment='商品SKU分组')
    sku_name: Mapped[str] = Column('Fsku_name', String(1024), index=True, comment='商品名称')
    inventory: Mapped[int] = Column('Finventory', Integer, default=0, server_default="0",
                                    comment='库存量')
    erp_sku_name: Mapped[str] = Column('Ferp_sku_name', String(1024), index=True, comment='ERP商品名称')
    erp_sku_image_url: Mapped[str] = Column('Ferp_sku_image_url', String(10240), comment='商品图片链接')
    erp_sku_id: Mapped[str] = Column('Ferp_sku_id', String(256), comment='erp上sku id')
    erp_sku_info: Mapped[dict] = Column('Ferp_sku_info', JSON, comment='erp上商品扩展信息')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0",
                                    comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0",
                                  comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="",
                                      comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='创建时间')
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='修改时间')
    columns = [
        "project_id", "sku", "sku_group",
        "sku_name", "inventory", "erp_sku_name", "erp_sku_image_url",
        "erp_sku_id", "erp_sku_info",
        "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]


class SkuPurchasePriceDto(DtoBase):
    """
    商品SKU采购价
    """
    __tablename__ = "t_sku_purchase_price"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Fsku", "Fsupplier_id"
    ), {
                          "mysql_default_charset": "utf8"
                      })
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    sku: Mapped[str] = Column('Fsku', String(256), comment='商品SKU')
    supplier_id: Mapped[int] = Column('Fsupplier_id', Integer, comment='供应商id')
    supplier_name: Mapped[str] = Column('Fsupplier_name', String(128), index=True, comment='供应商名')
    purchase_price: Mapped[int] = Column('Fpurchase_price', Integer, comment='供应价')
    sku_group: Mapped[str] = Column('Fsku_group', String(256), index=True, comment='商品SKU分组')
    sku_name: Mapped[str] = Column('Fsku_name', String(1024), index=True, comment='商品名称')
    erp_sku_image_url: Mapped[str] = Column('Ferp_sku_image_url', String(10240), comment='商品图片链接')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0",
                                    comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0",
                                  comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="",
                                      comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='创建时间')
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='修改时间')
    columns = [
        "project_id", "sku", "supplier_id", "supplier_name", "sku_group",
        "sku_name", "erp_sku_image_url", "purchase_price",
        "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]


class PurchaseOrder(DtoBase):
    """
    商品SKU采购价
    """
    __tablename__ = "t_purchase_order"
    __table_args__ = ({
        "mysql_default_charset": "utf8"
    })
    purchase_order_id: Mapped[int] = Column('Fpurchase_order_id', Integer, primary_key=True, autoincrement=True,
                                            comment="采购单id")
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    supplier_id: Mapped[int] = Column('Fsupplier_id', Integer, comment='供应商id')
    supplier_name: Mapped[str] = Column('Fsupplier_name', String(128), index=True, comment='供应商名')
    # 采购步骤主要有：
    # 草稿
    # 供应商捡货中
    # 待发货
    # 已入库
    # 完成
    # 废弃
    purchase_step: Mapped[str] = Column('Fpurchase_step', String(128), index=True, comment='采购状态')
    sku_summary: Mapped[str] = Column('Fsku_summary', String(10240), default="", server_default="", comment='货物概述')
    sku_amount: Mapped[int] = Column('Fsku_amount', Integer, default=0, server_default="0", comment='sku采购金额')
    pay_amount: Mapped[int] = Column('Fpay_amount', Integer, default=0, server_default="0", comment='支付金额')
    pay_state: Mapped[int] = Column('Fpay_state', Integer, default=0, server_default="0",
                                    comment='支付状态，0： 未支付， 1：已支付')
    purchase_date: Mapped[str] = Column('Fpurchase_date', String(128), index=True, comment='采购日期')
    expect_arrive_warehouse_date: Mapped[str] = Column('Fexpect_arrive_warehouse_date', String(128), index=True,
                                                       comment='预计到货日期')
    maritime_port: Mapped[str] = Column('Fmaritime_port', String(128), index=True, comment='海运港口')
    shipping_company: Mapped[str] = Column('Fshipping_company', String(128), index=True, comment='货运公司')
    shipping_fee: Mapped[str] = Column('Fshipping_fee', String(128), comment='海运费')
    arrive_warehouse_date: Mapped[str] = Column('Farrive_warehouse_date', String(128), index=True, comment='入库日期')
    remark: Mapped[str] = Column('Fremark', String(10240), default="", server_default="", comment='备注')
    """ 
    purchase_skus: [
        {
            "sku": "",
            "sku_group": "",
            "sku_name": "",
            "unit_price": 1200,
            "quantity"： 30
        }
    ]
    """
    purchase_skus: Mapped[list] = Column('Fpurchase_skus', JSON, comment='采购的货品')
    """ 
    store_skus: [
        {
            "sku": "",
            "sku_group": "",
            "sku_name": "",
            "quantity"： 30,
            "check_in_quantity"： 30,
        }
    ]
    """
    store_skus: Mapped[list] = Column('Fstore_skus', JSON, comment='入库的货品')
    op_log: Mapped[list] = Column('op_log', JSON, comment='操作记录')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0",
                                    comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0",
                                  comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="",
                                      comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='创建时间')
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='修改时间')
    columns = [
        "purchase_order_id", "project_id", "supplier_id", "supplier_name",
        "purchase_step", "sku_summary", "sku_amount", "pay_amount", "pay_state", "purchase_date",
        "expect_arrive_warehouse_date", "maritime_port", "shipping_company",
        "shipping_fee", "arrive_warehouse_date",
        "remark", "purchase_skus", "store_skus", "op_log",
        "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]


class MysqlBackend(object):
    """
        状态后端接口
        """

    def __init__(self, project_id: str, host: str, port: int,
                 user: str, password: str, db_name: str = "ec_erp_db") -> None:
        """

        :param project_id: 项目id， 如果为None或者空，则只能查询非项目私有资源
        :param host: mysql host
        :param port: mysql port
        :param user: mysql 用户
        :param password:  mysql 密码
        :param db_name: 数据库名，默认： fptool_db
        """
        self.project_id = project_id
        port = int(port)

        self.db_engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8",
                                       echo=True)
        self.check_db_engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}?charset=utf8",
                                             echo=True)

        self.check_db_engine.logger = logging.getLogger("sqlalchemy")
        self.db_name = db_name
        self.DBSession = sessionmaker(bind=self.db_engine)

    def init_backend(self):
        """
        初始化存储后端，例如创建库表等
        :return:
        """
        self.init_db()

    def init_db(self):
        # prepare database
        with self.check_db_engine.connect() as con:
            # Query for existing databases
            existing_databases = con.execute(text('SHOW DATABASES;'))
            # Results are a list of single item tuples, so unpack each tuple
            existing_databases = [d[0] for d in existing_databases]

            # Create database if not exists
            if self.db_name not in existing_databases:
                con.execute(text("CREATE DATABASE {0}".format(self.db_name)))
                logging.info("Created database {0}".format(self.db_engine))
        # init all tables
        DtoBase.metadata.create_all(self.db_engine)

    @staticmethod
    def _get_project(session, project_id: str) -> typing.Tuple[typing.Optional[dict], typing.Optional[ProjectDto]]:
        """
        获取project_id的项目配置
        :param project_id:
        :return: ProjectConfig.to_dict()
        """
        try:
            record: ProjectDto = session.query(ProjectDto).filter(
                ProjectDto.project_id == project_id).one()
            return record.doc, record
        except NoResultFound:
            return None, None

    def store_project(self, project_id: str, project: dict):
        session = self.DBSession()
        try:
            # 查询db是否有这个记录
            instance, db_dto = self._get_project(session, project_id)
            # 备份记录
            if instance is not None:
                db_dto.version += 1
                db_dto.doc = project
                db_dto.modify_time = datetime.now()
                session.add(db_dto)
            else:
                # 构建新的dto
                db_dto = ProjectDto(project_id=project_id,
                                    doc=project,
                                    is_delete=0,
                                    version=0,
                                    create_time=datetime.now(),
                                    modify_time=datetime.now()
                                    )
                session.add(db_dto)
            # 提交事务
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            logging.error(f"store project project_id {project_id}"
                          f"  failed: {e}")
            raise

    @staticmethod
    def _get_user(session, user_name: str) -> typing.Optional[UserDto]:
        """
        获取用户信息
        :param user_name:
        :return: UserDto
        """
        try:
            record: UserDto = session.query(UserDto).filter(
                UserDto.user_name == user_name).one()
            return record
        except NoResultFound:
            return None

    def store_user(self, user: UserDto):
        session = self.DBSession()
        try:
            # 查询db是否有这个记录
            db_dto = self._get_user(session, user.user_name)
            # 备份记录
            if db_dto is not None:
                user.create_time = db_dto.create_time
                DtoUtil.copy(user, db_dto)
                db_dto.modify_time = datetime.now()
                session.add(db_dto)
            else:
                # 构建新的dto
                user.create_time = datetime.now()
                user.modify_time = datetime.now()
                session.add(user)
            # 提交事务
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            logging.error(f"store user user_name {user.user_name}"
                          f"  failed: {e}")
            raise

    def get_user(self, user_name: str) -> typing.Optional[UserDto]:
        session = self.DBSession()
        try:
            # 查询db是否有这个记录
            db_dto = self._get_user(session, user_name)
            session.close()
            return db_dto
        except Exception as e:
            session.close()
            logging.error(f"get user user_name {user_name}"
                          f"  failed: {e}")
            raise

    @staticmethod
    def _get_supplier(session, supplier_id: int) -> typing.Optional[SupplierDto]:
        try:
            record: SupplierDto = session.query(SupplierDto).filter(
                SupplierDto.supplier_id == supplier_id).one()
            return record
        except NoResultFound:
            return None

    def store_supplier(self, supplier: SupplierDto):
        session = self.DBSession()
        try:
            # 查询db是否有这个记录
            if supplier.supplier_id > 0:
                db_dto = self._get_supplier(session, supplier.supplier_id)
            else:
                db_dto = None
            # 备份记录
            if db_dto is not None:
                supplier.create_time = db_dto.create_time
                DtoUtil.copy(supplier, db_dto)
                db_dto.modify_time = datetime.now()
                session.add(db_dto)
            else:
                # 构建新的dto
                supplier.create_time = datetime.now()
                supplier.modify_time = datetime.now()
                supplier.supplier_id = None
                session.add(supplier)
            # 提交事务
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            logging.error(f"store user user_name {supplier.supplier_name}"
                          f"  failed: {e}")
            raise

    def search_suppliers(self, offset: int, limit: int) -> typing.Tuple[int, typing.List[SupplierDto]]:
        session = self.DBSession()
        q = session.query(SupplierDto).filter(SupplierDto.project_id == self.project_id).order_by(
            SupplierDto.supplier_id.asc())
        total = q.count()
        q = q.offset(offset).limit(limit)
        records = q.all()
        session.close()
        return total, records

    def _get_sku(self, session, sku: str) -> typing.Optional[SkuDto]:
        try:
            record: SkuDto = session.query(SkuDto).filter(SkuDto.project_id == self.project_id).filter(
                SkuDto.sku == sku).one()
            return record
        except NoResultFound:
            return None

    def store_sku(self, sku: SkuDto):
        if sku.project_id != self.project_id:
            raise Exception("sku project 非本项目数据")
        session = self.DBSession()
        try:
            # 查询db是否有这个记录
            db_dto = self._get_sku(session, sku.sku)
            # 备份记录
            if db_dto is not None:
                sku.create_time = db_dto.create_time
                DtoUtil.copy(sku, db_dto)
                db_dto.modify_time = datetime.now()
                session.add(db_dto)
            else:
                # 构建新的dto
                sku.create_time = datetime.now()
                sku.modify_time = datetime.now()
                session.add(sku)
            # 提交事务
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            logging.error(f"store sku sku {sku.sku}"
                          f"  failed: {e}")
            raise

    def search_sku(self, sku_group, sku_name, sku, offset: int, limit: int) -> typing.Tuple[int, typing.List[SkuDto]]:
        session = self.DBSession()
        q = session.query(SkuDto).filter(SkuDto.project_id == self.project_id)
        if sku_group is not None:
            q = q.filter(SkuDto.sku_group == sku_group)
        if sku_name is not None:
            q = q.filter(SkuDto.sku_name.like(f"%{sku_name}%"))
        if sku is not None:
            q = q.filter(SkuDto.sku.like(f"%{sku}%"))
        total = q.count()
        q = q.order_by(
            SkuDto.sku.asc()).offset(offset).limit(limit)
        records = q.all()
        session.close()
        return total, records

    def _get_sku_purchase_price(self, session, sku: str, supplier_id: int) -> typing.Optional[SkuPurchasePriceDto]:
        try:
            record: SkuPurchasePriceDto = session.query(SkuPurchasePriceDto).filter(
                SkuPurchasePriceDto.project_id == self.project_id
            ).filter(
                SkuPurchasePriceDto.sku == sku
            ).filter(
                SkuPurchasePriceDto.supplier_id == supplier_id
            ).one()
            return record
        except NoResultFound:
            return None

    def store_sku_purchase_price(self, sku_purchase: SkuPurchasePriceDto):
        if sku_purchase.project_id != self.project_id:
            raise Exception("sku project 非本项目数据")
        session = self.DBSession()
        try:
            # 查询db是否有这个记录
            db_dto = self._get_sku_purchase_price(session, sku_purchase.sku, sku_purchase.supplier_id)
            # 备份记录
            if db_dto is not None:
                sku_purchase.create_time = db_dto.create_time
                DtoUtil.copy(sku_purchase, db_dto)
                db_dto.modify_time = datetime.now()
                session.add(db_dto)
            else:
                # 构建新的dto
                sku_purchase.create_time = datetime.now()
                sku_purchase.modify_time = datetime.now()
                session.add(sku_purchase)
            # 提交事务
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            logging.error(f"store sku_purchase sku {sku_purchase.sku}"
                          f"  failed: {e}")
            raise

    def search_sku_purchase_price(self, offset, limit) -> typing.Tuple[int, typing.List[SkuPurchasePriceDto]]:
        session = self.DBSession()
        q = session.query(SkuPurchasePriceDto).filter(SkuPurchasePriceDto.project_id == self.project_id).order_by(
            SkuPurchasePriceDto.sku.asc())
        total = q.count()
        q = q.offset(offset).limit(limit)
        records = q.all()
        session.close()
        return total, records

    def _get_purchase_order(self, session, purchase_order_id: int) -> typing.Optional[PurchaseOrder]:
        try:
            record: PurchaseOrder = session.query(PurchaseOrder).filter(
                PurchaseOrder.project_id == self.project_id
            ).filter(
                PurchaseOrder.purchase_order_id == purchase_order_id
            ).one()
            return record
        except NoResultFound:
            return None

    def store_purchase_order(self, purchase_order: PurchaseOrder):
        if purchase_order.project_id != self.project_id:
            raise Exception("sku project 非本项目数据")
        session = self.DBSession()
        try:
            # 查询db是否有这个记录
            if purchase_order.purchase_order_id >= 0:
                db_dto = self._get_purchase_order(session, purchase_order.purchase_order_id)
            else:
                db_dto = None
            # 备份记录
            if db_dto is not None:
                purchase_order.create_time = db_dto.create_time
                DtoUtil.copy(purchase_order, db_dto)
                db_dto.modify_time = datetime.now()
                session.add(db_dto)
            else:
                # 构建新的dto
                purchase_order.purchase_order_id = None
                purchase_order.create_time = datetime.now()
                purchase_order.modify_time = datetime.now()
                session.add(purchase_order)
            # 提交事务
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            logging.error(f"store purchase_order order_id {purchase_order.purchase_order_id}"
                          f"  failed: {e}")
            raise

    def search_purchase_order(self, offset, limit) -> typing.Tuple[int, typing.List[PurchaseOrder]]:
        session = self.DBSession()
        q = session.query(PurchaseOrder).filter(PurchaseOrder.project_id == self.project_id).order_by(
            PurchaseOrder.purchase_order_id.desc())
        total = q.count()
        q = q.offset(offset).limit(limit)
        records = q.all()
        session.close()
        return total, records

    def get_supplier(self, supplier_id: int) -> typing.Optional[SupplierDto]:
        session = self.DBSession()
        supplier = self._get_supplier(session, supplier_id)
        session.close()
        return supplier

    def get_sku(self, sku: str) -> typing.Optional[SkuDto]:
        session = self.DBSession()
        sku = self._get_sku(session, sku)
        session.close()
        return sku

    def get_sku_purchase_price(self, supplier_id: int, sku: str) -> typing.Optional[SkuPurchasePriceDto]:
        session = self.DBSession()
        price = self._get_sku_purchase_price(session, sku, supplier_id)
        session.close()
        return price


def main():
    backend = MysqlBackend(
        "dev", "9.134.78.50", 3307, "zft_dev_all", "zft_dev_all"
    )
    # 创建库表
    backend.init_db()
    # 创建项目
    backend.store_project("dev", {
        "project_id": "dev",
        "project_name": "开发环境",
        "project_config": {}
    })
    backend.store_user(UserDto(
        user_name="jk",
        default_project_id="dev",
        password=codec_util.calc_sha256("jktest_2024"),
        roles=[
            {
                "project_id": "dev",
                "name": "supply",
                "memo": "供应链管理",
                "level": 1
            },
            {
                "project_id": "dev",
                "name": "storehouse",
                "memo": "仓库管理",
                "level": 1
            }
        ],
        is_admin=1
    ))
    print(json.dumps(DtoUtil.to_dict(backend.get_user("jk")), indent=2, ensure_ascii=False))
    backend.store_supplier(SupplierDto(
        supplier_id=-1,
        project_id="dev",
        supplier_name="草地厂家(子龙)",
        wechat_account="-zilong",
        detail="""6212260408009471538 中国工商银行 宗子龙
18531712555"""
    ))
    backend.store_sku(SkuDto(
        project_id="dev",
        sku="G-2-grape leaves",
        sku_group="藤条/假花/假叶子/藤条类型/一条的藤条（最基础）",
        sku_name="葡萄叶",
        inventory=8926,
        erp_sku_name="葡萄叶",
        erp_sku_image_url="https://res.bigseller.pro/static/images/merchantsku/279590/14556627_1656647069034.jpg?imageView2/1/w/300/h/300",
        erp_sku_id="28439992",
        erp_sku_info={
            "test_key": "test_v"
        }
    ))
    backend.store_sku(SkuDto(
        project_id="dev",
        sku="G-3-watermelon leaves",
        sku_group="藤条/假花/假叶子/藤条类型/一条的藤条（最基础）",
        sku_name="西瓜叶子",
        inventory=9038,
        erp_sku_name="西瓜叶子-1条",
        erp_sku_image_url="https://res.bigseller.pro/static/images/merchantsku/279590/1656646733593.jpg?imageView2/1/w/300/h/300",
        erp_sku_id="28439992",
        erp_sku_info={
            "test_key": "test_v"
        }
    ))
    backend.store_sku(SkuDto(
        project_id="dev",
        sku="G-4-green dill leaves",
        sku_group="藤条/假花/假叶子/藤条类型/一条的藤条（最基础）",
        sku_name="绿萝叶子",
        inventory=7029,
        erp_sku_name="绿萝叶子-1条",
        erp_sku_image_url="https://res.bigseller.pro/static/images/merchantsku/279590/1656646779124.jpg?imageView2/1/w/300/h/300",
        erp_sku_id="28439992",
        erp_sku_info={
            "test_key": "test_v"
        }
    ))
    backend.store_sku(SkuDto(
        project_id="dev",
        sku="CW-16-2*0.5m",
        sku_group="茅草/2m宽度",
        sku_name="一平米茅草",
        inventory=1436,
        erp_sku_name="一平米茅草",
        erp_sku_image_url="https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/20231023113418099c269da354dc6bf0329dd263c57705.png?imageView2/1/w/300/h/300",
        erp_sku_id="21575327",
        erp_sku_info={
            "test_key": "test_v"
        }
    ))
    backend.store_sku_purchase_price(SkuPurchasePriceDto(
        project_id="dev",
        sku="G-2-grape leaves",
        supplier_id=1,
        supplier_name="草地厂家(子龙)",
        purchase_price=102,
        erp_sku_image_url="https://res.bigseller.pro/static/images/merchantsku/279590/14556627_1656647069034.jpg?imageView2/1/w/300/h/300",
        sku_group="藤条/假花/假叶子/藤条类型/一条的藤条（最基础）",
        sku_name="葡萄叶-1条",
    ))


if __name__ == '__main__':
    main()
