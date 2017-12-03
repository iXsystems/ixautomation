# Created by: Joe Maloney <jmaloney@ixsystems.com>

PORTNAME=	pc-updatemanager
PORTVERSION=	%%CHGVERSION%%
CATEGORIES=	sysutils

MAINTAINER=	jmaloney@ixsystems.com
COMMENT=	iXsystems automation framework

LICENSE=	BSD2CLAUSE

RUN_DEPENDS=	${LOCALBASE}/bin/vm:sysutils/vm-bhyve

WRKSRC_SUBDIR=  src
USES=		python:3.6
MAKE_ARGS=	PREFIX=${STAGEDIR}${PREFIX}

USE_GITHUB=	yes
GH_ACCOUNT=	ixsystems
GH_PROJECT=	ixautomation
GH_TAGNAME=	%%GHTAG%%

.include <bsd.port.mk>
