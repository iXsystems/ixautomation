# Created by: Joe Maloney <jmaloney@ixsystems.com>
# $FreeBSD$

PORTNAME=	ixautomation
PORTVERSION=	%%CHGVERSION%%
CATEGORIES=	sysutils

MAINTAINER=	jmaloney@ixsystems.com
COMMENT=	Automation framework for iXsystems projects

LICENSE=	BSD2CLAUSE

RUN_DEPENDS=	${LOCALBASE}/sbin/vm:sysutils/vm-bhyve \
		${LOCALBASE}/bin/expect:lang/expect \
		${LOCALBASE}/bin/geckodriver:www/geckodriver

WRKSRC_SUBDIR=  src
USES=		python:3.6
USE_PYTHON=	distutils pytest requests pip
MAKE_ARGS=	PREFIX=${STAGEDIR}${PREFIX}

USE_GITHUB=	yes
GH_ACCOUNT=	ixsystems
GH_PROJECT=	ixautomation
GH_TAGNAME=	%%GHTAG%%

.include <bsd.port.mk>